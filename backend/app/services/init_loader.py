from datetime import date, timedelta, datetime
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.models.law import Law
from app.models.law_change_event import LawChangeEvent
from app.models.old_new_info import OldNewInfo
from app.models.article_diff import ArticleDiff
from app.services.nlic_client import fetch_law_history_page_by_regdt, fetch_old_new


def _parse_ymd(s: str | None) -> date | None:
    if not s:
        return None
    s = str(s).replace("-", "")
    if len(s) != 8:
        return None
    return datetime.strptime(s, "%Y%m%d").date()


def _upsert_law(db: Session, item: Dict[str, Any]) -> Law:
    """
    LawSearch.law[] → law 테이블 upsert

    필드:
      - 법령ID
      - 법령명한글
      - 법령구분명
      - 소관부처명
      - 소관부처코드
    """
    law_id = str(item.get("법령ID"))
    if not law_id:
        raise ValueError(f"법령ID 없음: {item}")

    law = db.get(Law, law_id)
    if not law:
        law = Law(law_id=law_id)
        db.add(law)

    law.law_name = item.get("법령명한글") or law.law_name
    law.law_type_name = item.get("법령구분명") or law.law_type_name
    law.ministry_names = item.get("소관부처명") or law.ministry_names
    law.ministry_codes = item.get("소관부처코드") or law.ministry_codes

    return law

def _ensure_list(v) -> List[Dict[str, Any]]:
    """old/new 조문 목록이 dict로 오든 list로 오든 항상 list[dict]로 변환"""
    if not v:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, dict):
        return [v]
    # 혹시 모를 이상한 타입 방지용
    return []

def _create_change_event_if_new(
    db: Session,
    law: Law,
    item: Dict[str, Any],
    reg_dt: date,
) -> LawChangeEvent | None:
    """
    LawSearch.law[] → law_change_event 신규 생성

    필드:
      - 법령일련번호 → mst
      - 제개정구분명 → change_type
      - 공포번호 → proclamation_no
      - 공포일자 → proclamation_date
      - 시행일자 → enforce_date
      - 현행연혁코드 → current_hist_cd
    """
    mst_raw = item.get("법령일련번호")
    if not mst_raw:
        return None

    mst = str(mst_raw)

    existing = (
        db.query(LawChangeEvent)
        .filter(
            LawChangeEvent.law_id == law.law_id,
            LawChangeEvent.mst == mst,
        )
        .first()
    )
    if existing:
        return None

    change_type = item.get("제개정구분명")
    proclamation_no = item.get("공포번호")
    proclamation_date = _parse_ymd(item.get("공포일자"))
    enforce_date = _parse_ymd(item.get("시행일자"))
    current_hist_cd = item.get("현행연혁코드")

    event = LawChangeEvent(
        law_id=law.law_id,
        mst=mst,
        change_type=change_type,
        proclamation_no=proclamation_no,
        proclamation_date=proclamation_date,
        enforce_date=enforce_date,
        current_hist_cd=current_hist_cd,
        collected_date=reg_dt,
    )
    db.add(event)
    db.flush()  # change_id 확보

    return event


def _save_old_new_and_articles(db: Session, event: LawChangeEvent) -> None:
    """
    oldAndNew 호출 → old_new_info + article_diff 적재
    """
    # 이미 있으면 스킵
    existing = db.get(OldNewInfo, event.change_id)
    if existing:
        return

    data = fetch_old_new(event.mst)

    service = data.get("OldAndNewService") or data

    old_basic = service.get("구조문_기본정보") or {}
    new_basic = service.get("신조문_기본정보") or {}

    # ✅ 조문목록이 dict일 수도, list일 수도 있으므로 normalize
    raw_old = (service.get("구조문목록") or {}).get("조문")
    raw_new = (service.get("신조문목록") or {}).get("조문")

    old_list: List[Dict[str, Any]] = _ensure_list(raw_old)
    new_list: List[Dict[str, Any]] = _ensure_list(raw_new)

    has_old_new = "Y" if (old_list or new_list) else "N"

    info = OldNewInfo(
        change_id=event.change_id,
        has_old_new=has_old_new,
        old_basic=old_basic,
        new_basic=new_basic,
    )
    db.add(info)
    db.flush()

    max_len = max(len(old_list), len(new_list))

    for i in range(max_len):
        old_item = old_list[i] if i < len(old_list) else {}
        new_item = new_list[i] if i < len(new_list) else {}

        old_no = old_item.get("no")
        new_no = new_item.get("no")

        old_content = old_item.get("content") or ""
        new_content = new_item.get("content") or ""

        diff = ArticleDiff(
            change_id=event.change_id,
            old_no=old_no,
            old_content=old_content,
            new_no=new_no,
            new_content=new_content,
        )
        db.add(diff)
        
def load_changes_for_date(db: Session, target_date: date) -> Dict[str, Any]:
    """
    특정 날짜(target_date)의 regDt 변경이력을 모두 수집해서
    law / law_change_event / old_new_info / article_diff 에 적재.

    배치(매일 밤 어제분)에서 재사용할 핵심 함수.
    """
    total_history_records = 0
    total_new_events = 0
    total_laws_touched = 0

    page = 1
    while True:
        items, has_next = fetch_law_history_page_by_regdt(
            reg_dt=target_date,
            page=page,
            display=100,
        )

        if not items:
            break

        for item in items:
            total_history_records += 1

            # law upsert
            law = _upsert_law(db, item)
            db.flush()
            total_laws_touched += 1

            # law_change_event 신규 생성
            event = _create_change_event_if_new(
                db=db,
                law=law,
                item=item,
                reg_dt=target_date,
            )
            if not event:
                continue

            total_new_events += 1

            # old/new + article_diff 적재
            _save_old_new_and_articles(db, event)

        db.commit()

        if not has_next:
            break
        page += 1

    return {
        "target_date": target_date.isoformat(),
        "total_history_records_seen": total_history_records,
        "total_new_events_inserted": total_new_events,
        "total_laws_touched": total_laws_touched,
    }


def load_initial_changes_until_yesterday(
    db: Session,
    start_date: date | None = None,
) -> Dict[str, Any]:
    """
    (start_date ~ 어제까지) 전체 적재 – 기존 함수는 그대로 두고 사용.
    """
    if start_date is None:
        start_date = date(1990, 1, 1)

    end_date = date.today() - timedelta(days=1)

    total_history_records = 0
    total_new_events = 0
    total_laws_touched = 0

    cur = start_date
    while cur <= end_date:
        daily_summary = load_changes_for_date(db, cur)

        total_history_records += daily_summary["total_history_records_seen"]
        total_new_events += daily_summary["total_new_events_inserted"]
        total_laws_touched += daily_summary["total_laws_touched"]

        cur += timedelta(days=1)

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_history_records_seen": total_history_records,
        "total_new_events_inserted": total_new_events,
        "total_laws_touched": total_laws_touched,
    }
