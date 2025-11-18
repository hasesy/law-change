# app/api/v1/endpoints/changes.py
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db   
from app.models.law import Law
from app.models.law_change_event import LawChangeEvent
from app.models.old_new_info import OldNewInfo
from app.models.article_diff import ArticleDiff
from app.schemas.law_change import (
    LawChangeListResponse,
    LawChangeListItem,
    LawChangeDetail,
    LawChangeSummary,
    ArticleDiffItem,
)

router = APIRouter()


@router.get("", response_model=LawChangeListResponse)
def list_law_changes(
    db: Session = Depends(get_db),
    keyword: Optional[str] = Query(None, description="법령명 검색어"),
    date_basis: str = Query(
        "promulgation", description="promulgation | enforcement | collected"
    ),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(6, ge=1, le=100),
):
    """
    변경이력 목록 조회

    - keyword: 법령명 like 검색
    - date_basis:
        - promulgation: 공포일자 (proclamation_date)
        - enforcement: 시행일자 (enforce_date)
        - collected: 변경일자 (collected_date)
    - start_date, end_date: 기준일자 범위
    - page, page_size: 페이지네이션
    """
    # 기준 날짜 컬럼 매핑
    if date_basis == "enforcement":
        # 시행일자
        date_column = LawChangeEvent.enforce_date
    elif date_basis == "collected":
        # 변경일자
        date_column = LawChangeEvent.collected_date
    else:
        # 기본: 공포일자
        date_column = LawChangeEvent.proclamation_date

    q = db.query(LawChangeEvent, Law).join(Law, Law.law_id == LawChangeEvent.law_id)

    if keyword:
        like = f"%{keyword}%"
        q = q.filter(Law.law_name.ilike(like))

    if start_date:
        q = q.filter(date_column >= start_date)
    if end_date:
        q = q.filter(date_column <= end_date)

    total = q.count()

    offset = (page - 1) * page_size
    rows = (
        q.order_by(
            date_column.desc().nullslast(),
            LawChangeEvent.created_at.desc(),
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items: list[LawChangeListItem] = []

    for ev, law in rows:
        items.append(
            LawChangeListItem(
                change_id=ev.change_id,
                law_id=ev.law_id,
                law_name=law.law_name,
                law_type_name=law.law_type_name,
                ministry_names=law.ministry_names,
                change_type=ev.change_type,
                proclamation_no=ev.proclamation_no,
                proclamation_date=ev.proclamation_date,
                enforce_date=ev.enforce_date,
                current_hist_cd=ev.current_hist_cd,
                collected_date=ev.collected_date,  # ✅ 변경일자
                change_summary=ev.change_summary,
                action_recommendation=ev.action_recommendation,
                ai_importance=ev.ai_importance
            )
        )

    return LawChangeListResponse(total=total, items=items)


@router.get("/{change_id}", response_model=LawChangeDetail)
def get_law_change_detail(
    change_id: UUID,
    db: Session = Depends(get_db),
):
    """
    특정 change_id에 대한
    - 법령/변경이력 요약
    - 신·구 기본정보
    - 조문 비교 목록

    최종 URL: GET /api/v1/changes/{change_id}
    """
    # 변경 이벤트 + 법령 기본정보
    row = (
        db.query(LawChangeEvent, Law)
        .join(Law, Law.law_id == LawChangeEvent.law_id)
        .filter(LawChangeEvent.change_id == change_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Change event not found")

    ev, law = row
    mst = ev.mst  # 🔑 이후 조회는 전부 MST 기준

    change_summary = LawChangeSummary(
        change_id=ev.change_id,
        law_id=ev.law_id,
        law_name=law.law_name,
        law_type_name=law.law_type_name,
        ministry_names=law.ministry_names,
        change_type=ev.change_type,
        proclamation_no=ev.proclamation_no,
        proclamation_date=ev.proclamation_date,
        enforce_date=ev.enforce_date,
        collected_date=ev.collected_date,
        change_summary=ev.change_summary,
        action_recommendation=ev.action_recommendation,
        ai_importance=ev.ai_importance
    )

     # 2) 신·구 기본정보 (mst 기준으로 1건)
    oni: Optional[OldNewInfo] = (
        db.query(OldNewInfo)
        .filter(OldNewInfo.mst == mst)
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

    # 조문 비교 목록
    article_rows = (
        db.query(ArticleDiff)
        .filter(ArticleDiff.mst == mst)
        .order_by(
            ArticleDiff.old_no.nullsfirst(),
            ArticleDiff.new_no.nullsfirst(),
            ArticleDiff.diff_id,
        )
        .all()
    )

    articles = [ArticleDiffItem.from_orm(a) for a in article_rows]

    return LawChangeDetail(
        change=change_summary,
        has_old_new=has_old_new,
        old_basic=old_basic,
        new_basic=new_basic,
        articles=articles,
    )
