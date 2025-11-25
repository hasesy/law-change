# app/api/v1/endpoints/admin_rules.py
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import get_settings

from app.db.session import get_db
from app.models.admin_rule import AdminRule, AdminRuleList
from app.schemas.admin_rule import AdminRuleListItem, AdminRuleListResponse
from app.enums.admin_rule_category import AdminRuleCategory

router = APIRouter()

settings = get_settings()


@router.get("", response_model=AdminRuleListResponse)
def list_admin_rules(
    db: Session = Depends(get_db),
    keyword: Optional[str] = Query(None, description="행정규칙명 검색어"),
    category: Optional[AdminRuleCategory] = Query(
        None, description="CHEMICAL / PSM / DANGER / ENV / HEALTH / FIRE / ETC"
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
    if category:
        q = q.filter(AdminRule.category == category)

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
                detail_link_path=f"/admin-rules/{lst.admrul_sn}/view",
            )
        )

    return AdminRuleListResponse(total=total, items=items)


@router.get("/{admrul_sn}/view")
def view_admin_rule(
    admrul_sn: str,
):
    """
    행정규칙 본문 보기 프록시.
    브라우저에는 이 URL만 노출되고,
    실제 DRF 호출 시에는 서버에서 OC를 붙여서 리다이렉트한다.
    """
    oc = settings.nlic_oc

    if not oc:
        raise HTTPException(status_code=500, detail="OC is not configured")

    drf_url = (
        "https://www.law.go.kr/DRF/lawService.do"
        f"?OC={oc}&target=admrul&ID={admrul_sn}&type=HTML&mobileYn="
    )

    return RedirectResponse(drf_url)