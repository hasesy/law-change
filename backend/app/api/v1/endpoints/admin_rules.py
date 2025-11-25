# app/api/v1/endpoints/admin_rules.py
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import get_settings

from app.db.session import get_db
from app.models.admrul.admin_rule import AdminRule
from app.models.admrul.admin_rule_list import AdminRuleList
from app.models.admrul.admin_rule_old_new_info import AdminRuleOldNewInfo
from app.models.admrul.admin_rule_article_diff import AdminRuleArticleDiff
from app.schemas.admin_rule import AdminRuleListItem, AdminRuleListResponse, AdminRuleChangeDetail,AdminRuleSummary, AdminRuleArticleDiffItem
from app.enums.admin_rule_category import AdminRuleCategory

router = APIRouter()

settings = get_settings()


@router.get("", response_model=AdminRuleListResponse)
def list_admin_rules(
    db: Session = Depends(get_db),
    keyword: Optional[str] = Query(None, description="행정규칙명 검색어"),
    categories: Optional[List[AdminRuleCategory]] = Query(
        None,
        description="복수 카테고리: CHEMICAL / PSM / DANGER / ENV / HEALTH / FIRE / ETC",
    ),
    date_basis: str = Query(
        "issue",
        description="issue | enforce | created (발령일자 / 시행일자 / 생성일자 기준)",
        regex="^(issue|enforce|created)$",
    ),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    
    # 기본 쿼리: 목록 + 마스터 조인 (category 필터 위해)
    q = (
        db.query(AdminRuleList, AdminRule)
        .join(AdminRule, AdminRuleList.admrul_id == AdminRule.admrul_id)
    )

    # 검색어
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(AdminRuleList.admrul_name.ilike(like))

    # 카테고리
    if categories:
        q = q.filter(AdminRule.category.in_(categories))

    # 기준일자 컬럼 선택
    if date_basis == "issue":
        date_col = AdminRuleList.issue_date
    elif date_basis == "enforce":
        date_col = AdminRuleList.enforce_date
    else:  # created
        date_col = AdminRuleList.nlic_registered_date

    # 기간 필터
    if start_date:
        q = q.filter(date_col >= start_date)
    if end_date:
        q = q.filter(date_col <= end_date)

    total = q.count()
    

    rows = (
        q.order_by(date_col.desc().nullslast())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items: list[AdminRuleListItem] = []
    for lst, master in rows:
        items.append(
            AdminRuleListItem(
                admrul_sn=lst.admrul_sn,
                admrul_id=lst.admrul_id,
                admrul_name=lst.admrul_name,
                admrul_type_name=lst.admrul_type_name,
                ministry_names=master.ministry_names,
                category=master.category,
                issue_date=lst.issue_date,
                enforce_date=lst.enforce_date,
                nlic_registered_date=lst.nlic_registered_date,
                issue_number=lst.issue_number,
                change_type_name=lst.change_type_name,
                current_history_type=lst.current_history_type,
                detail_link_path=f"/admin-rules/{lst.admrul_sn}/view",
                change_summary=lst.change_summary,
            )
        )

    return AdminRuleListResponse(total=total, items=items)


@router.get("/{admrul_sn}", response_model=AdminRuleChangeDetail)
def get_admin_rule_detail(
    admrul_sn: str,
    db: Session = Depends(get_db),
):
    """
    행정규칙 1건 + 신·구법 기본정보 + 조문 비교 목록

    최종 URL 예시:
      GET /api/v1/admin-rules/{admrul_sn}
    """
    # 1) 행정규칙 마스터 조회 (신규 테이블/뷰면 거기에 맞게 수정)
    row = (
        db.query(AdminRuleList, AdminRule)
        .join(AdminRule, AdminRuleList.admrul_id == AdminRule.admrul_id)
        .filter(AdminRuleList.admrul_sn == admrul_sn)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Admin rule not found")

    lst, master = row
    # 🔑 법령과 동일하게 MST 기준으로 Old/New, diff 묶인다고 가정

    # 상단 요약용
    rule_summary = AdminRuleSummary(
        admrul_sn=lst.admrul_sn,
        admrul_id=lst.admrul_id,
        admrul_name=master.admrul_name,
        admrul_type_name=lst.admrul_type_name,
        ministry_names=master.ministry_names,
        category=master.category,
        change_type_name=lst.change_type_name,
        current_history_type=lst.current_history_type,
        issue_number=lst.issue_number,
        issue_date=lst.issue_date,
        enforce_date=lst.enforce_date,
        change_summary=lst.change_summary,
        action_recommendation=lst.action_recommendation,
        ai_importance=lst.ai_importance,
    )

    # 2) 신·구 기본정보 (mst 기준 1건)
    oni: Optional[AdminRuleOldNewInfo] = (
        db.query(AdminRuleOldNewInfo)
        .filter(AdminRuleOldNewInfo.admrul_sn == admrul_sn)
        .first()
    )

    if oni is None:
        has_old_new = "N"
        old_basic = None
        new_basic = None
    else:
        has_old_new = oni.has_old_new
        old_basic = oni.old_basic
        new_basic = oni.new_basic

    # 3) 조문 비교 목록
    article_rows = (
        db.query(AdminRuleArticleDiff)
        .filter(AdminRuleArticleDiff.admrul_sn == admrul_sn)
        .order_by(
            AdminRuleArticleDiff.old_no.nullsfirst(),
            AdminRuleArticleDiff.new_no.nullsfirst(),
            AdminRuleArticleDiff.diff_id,
        )
        .all()
    )

    articles = [AdminRuleArticleDiffItem.from_orm(a) for a in article_rows]

    return AdminRuleChangeDetail(
        rule=rule_summary,
        has_old_new=has_old_new,
        old_basic=old_basic,
        new_basic=new_basic,
        articles=articles,
    )