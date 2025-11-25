# app/services/admin_rule_service.py

from datetime import date
from typing import Dict, Any, List, Tuple

from sqlalchemy.orm import Session

from app.models.admrul.admin_rule import AdminRule
from app.models.admrul.admin_rule_list import AdminRuleList
from app.models.admrul.admin_rule_old_new_info import AdminRuleOldNewInfo
from app.models.admrul.admin_rule_article_diff import AdminRuleArticleDiff

from app.services.nlic_client import (
    fetch_admin_rule_page_by_issue_range,
    fetch_admin_rule_old_new
)
from app.services.common import parse_ymd, ensure_list_dict
from app.services.categorizer import classify_admin_rule


def _upsert_admin_rule(db: Session, item: Dict[str, Any]) -> tuple[AdminRule, bool]:
    """
    AdmRulSearch.admrul[] → admin_rule upsert
    return: (rule 객체, is_new)
    """
    admrul_id_raw = item.get("행정규칙ID")
    if not admrul_id_raw:
        raise ValueError(f"행정규칙ID 없음: {item}")

    admrul_id = int(admrul_id_raw)
    admrul_name = item.get("행정규칙명") or ""

    rule = db.get(AdminRule, admrul_id)
    is_new = False

    if not rule:
        rule = AdminRule(admrul_id=admrul_id)
        db.add(rule)
        is_new = True  # ✅ 여기서만 True

    # upsert 필드 업데이트
    rule.admrul_name = admrul_name or rule.admrul_name
    rule.admrul_type_name = item.get("행정규칙종류") or rule.admrul_type_name
    rule.ministry_names = item.get("소관부처명") or rule.ministry_names

    # ✅ 카테고리 분류/세팅
    category = classify_admin_rule(str(admrul_id), admrul_name)
    rule.category = category

    return rule, is_new


def _create_admin_rule_list_if_new(
    db: Session,
    item: Dict[str, Any],
) -> AdminRuleList | None:
    """
    AdmRulSearch.admrul[] → admin_rule_list 신규 생성
    - PK: 행정규칙일련번호(admrul_sn)
    - 이미 있으면 None 리턴
    """
    admrul_sn = item.get("행정규칙일련번호")
    if not admrul_sn:
        return None

    exists = db.get(AdminRuleList, admrul_sn)
    if exists:
        return None

    admrul_id = int(item.get("행정규칙ID"))
    admrul_name = item.get("행정규칙명") or ""
    admrul_type_name = item.get("행정규칙종류")

    current_history_type = item.get("현행연혁구분")
    change_type_code = item.get("제개정구분코드")
    change_type_name = item.get("제개정구분명")

    issue_date = parse_ymd(item.get("발령일자"))
    enforce_date = parse_ymd(item.get("시행일자"))
    nlic_registered_date = parse_ymd(item.get("생성일자"))

    issue_number = item.get("발령번호")
    detail_link_path = item.get("행정규칙상세링크")

    row = AdminRuleList(
        admrul_sn=admrul_sn,
        admrul_id=admrul_id,
        admrul_name=admrul_name,
        admrul_type_name=admrul_type_name,
        current_history_type=current_history_type,
        change_type_code=change_type_code,
        change_type_name=change_type_name,
        issue_date=issue_date,
        enforce_date=enforce_date,
        nlic_registered_date=nlic_registered_date,
        issue_number=issue_number,
        detail_link_path=detail_link_path,
        raw_json=item,
    )
    db.add(row)
    return row


def _save_old_new_and_articles_for_rule(
    db: Session,
    admrul_sn: str,
) -> Tuple[int, int]:
    """
    AdmRulOldAndNewService 호출 → admin_rule_old_new_info + admin_rule_article_diff 적재

    - admrul_sn(행정규칙일련번호) 단위로 한 번만 저장
    - 이미 old_new_info가 있으면 스킵
    return: (새로 insert된 old_new_info 개수, article_diff row 개수)
    """
    # 이미 있으면 스킵
    existing = db.get(AdminRuleOldNewInfo, admrul_sn)
    if existing:
        return 0, 0

    # NLIC DRF 호출 (AdmRulOldAndNewService)
    data = fetch_admin_rule_old_new(admrul_sn)

    service = data.get("AdmRulOldAndNewService") or data

    old_basic = service.get("구조문_기본정보") or {}
    new_basic = service.get("신조문_기본정보") or {}

    # 조문목록은 dict일 수도, list일 수도 있음 → normalize
    raw_old = (service.get("구조문목록") or {}).get("조문")
    raw_new = (service.get("신조문목록") or {}).get("조문")

    old_list: List[Dict[str, Any]] = ensure_list_dict(raw_old)
    new_list: List[Dict[str, Any]] = ensure_list_dict(raw_new)

    has_old_new = "Y" if (old_list or new_list) else "N"

    info = AdminRuleOldNewInfo(
        admrul_sn=admrul_sn,
        has_old_new=has_old_new,
        old_basic=old_basic,
        new_basic=new_basic,
    )
    db.add(info)
    db.flush()

    # 조문쌍 → diff 테이블에 저장
    max_len = max(len(old_list), len(new_list))
    diff_rows = 0

    for i in range(max_len):
        old_item = old_list[i] if i < len(old_list) else {}
        new_item = new_list[i] if i < len(new_list) else {}

        old_no = old_item.get("no")
        new_no = new_item.get("no")

        old_content = old_item.get("content") or ""
        new_content = new_item.get("content") or ""

        diff = AdminRuleArticleDiff(
            admrul_sn=admrul_sn,
            old_no=old_no,
            old_content=old_content,
            new_no=new_no,
            new_content=new_content,
        )
        db.add(diff)
        diff_rows += 1

    return 1, diff_rows


def load_admin_rules_for_period(
    db: Session,
    start_date: date,
    end_date: date,
    display: int = 100,
) -> Dict[str, Any]:
    """
    (start_date ~ end_date)의 발령일자 범위로 AdmRulSearch 페이지 조회 후

    - admin_rule (마스터) upsert
    - admin_rule_list (연혁/버전) insert
    - admin_rule_old_new_info + admin_rule_article_diff 적재

    를 한 번에 수행.
    """
    total_items = 0
    total_new_master = 0
    total_new_list = 0
    total_new_old_new_info = 0
    total_article_diff_rows = 0

    page = 1
    while True:
        items, has_next = fetch_admin_rule_page_by_issue_range(
            start_date=start_date,
            end_date=end_date,
            page=page,
            display=display,
        )

        if not items:
            break

        for item in items:
            total_items += 1

            # ✅ master upsert
            rule, is_new = _upsert_admin_rule(db, item)
            db.flush()
            if is_new:
                total_new_master += 1

            # ✅ list 신규 생성
            created = _create_admin_rule_list_if_new(db, item)
            if created:
                total_new_list += 1

                # 새로 생긴 버전에 대해서만 신·구 비교 API 호출
                # (이미 있는 admrul_sn이면 _save 함수에서 알아서 스킵)
                inserted_info, inserted_diff = _save_old_new_and_articles_for_rule(
                    db, created.admrul_sn
                )
                total_new_old_new_info += inserted_info
                total_article_diff_rows += inserted_diff

        db.commit()

        if not has_next:
            break
        page += 1

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_items_seen": total_items,
        "total_new_master": total_new_master,
        "total_new_list": total_new_list,
        "total_new_old_new_info": total_new_old_new_info,
        "total_article_diff_rows": total_article_diff_rows,
    }
