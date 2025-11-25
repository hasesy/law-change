# app/services/admin_rule_service.py
from datetime import date
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.admin_rule import AdminRule, AdminRuleList
from app.services.nlic_client import (
    fetch_admin_rule_page_by_issue_range,
)
from app.services.common import parse_ymd
from app.services.rule_categorizer import classify_admin_rule


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
    
    # ✅ 여기서 카테고리 분류/세팅
    #  - ID는 HARDCODED_CATEGORY_BY_ID로 우선 매칭
    #  - 아니면 제목 키워드로 매칭
    #  - 둘 다 아니면 ETC
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


def load_admin_rules_for_period(
    db: Session,
    start_date: date,
    end_date: date,
    display: int = 100,
) -> Dict[str, Any]:
    total_items = 0
    total_new_master = 0
    total_new_list = 0

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

            # ✅ 여기서 신규 여부를 정확히 알 수 있음
            rule, is_new = _upsert_admin_rule(db, item)
            db.flush()
            if is_new:
                total_new_master += 1

            created = _create_admin_rule_list_if_new(db, item)
            if created:
                total_new_list += 1

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
    }
