# app/api/v1/endpoints/dashboard.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardResponse, Importance
from app.services.dashboard_service import get_dashboard

router = APIRouter()


@router.get("", response_model=DashboardResponse)
def read_dashboard(
    days: int = Query(
        7,
        ge=1,
        le=90,
        description="조회 기간(일). 예: 7 / 15 / 30",
    ),
    min_importance: Importance = Query(
        "MEDIUM", description="최소 중요도 (HIGH | MEDIUM | LOW | NONE)"
    ),
    action_limit: int = Query(
        5, ge=1, le=20, description="주요 조치사항 최대 개수"
    ),
    db: Session = Depends(get_db),
):
    """
    대시보드 통합 API
      - 상단 개요 카드
      - 도메인별 요약 (안전/화학/환경, 고정 9개 법령)
      - 최근 중요 변경 이력 목록
      - 주요 조치사항
    """
    return get_dashboard(
        db=db,
        days=days,
        min_importance=min_importance,
        action_limit=action_limit,
    )
