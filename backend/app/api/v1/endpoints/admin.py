from typing import Dict, Any, Optional
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.nlic_law_change_loader import (load_initial_changes_until_yesterday, load_changes_for_date)
from app.services.nlic_admin_rule_loader import load_admin_rules_for_period


router = APIRouter()


@router.post("/law/init-changes")
def init_changes(
    start_date: Optional[date] = None,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    어제까지의 변경이력을 모두 저장하는 초기 전체 적재 API
    - start_date가 없으면 1990-01-01 ~ 어제까지
    """
    summary = load_initial_changes_until_yesterday(db, start_date=start_date)
    return summary



@router.post("/law/fetch-yesterday")
def fetch_yesterday(
    db: Session = Depends(get_db),
):
    """
    매일 밤 배치용 – '어제' 날짜(regDt=어제) 기준 변경이력 적재
    """
    target_date = date.today() - timedelta(days=1)
    summary = load_changes_for_date(db, target_date=target_date)
    return summary


@router.post("/law/fetch-date")
def fetch_for_date(
    target_date: date = Query(..., description="YYYY-MM-DD 형식의 날짜"),
    db: Session = Depends(get_db),
):
    """
    필요할 때 특정 날짜를 수동으로 다시 돌리고 싶을 때 쓰는 엔드포인트.
    예: /fetch-date?target_date=2025-11-11
    """
    summary = load_changes_for_date(db, target_date=target_date)
    return summary


@router.post("/rule/load/period")
def load_admin_rules_period(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    """
    행정규칙 발령일자 기간 기반 수동 적재 API
    - prmlYd=start_date~end_date
    """
    if start_date > end_date:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="start_date가 end_date보다 클 수 없습니다.")

    summary = load_admin_rules_for_period(db, start_date, end_date)
    return summary