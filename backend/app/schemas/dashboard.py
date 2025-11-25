# app/schemas/dashboard.py
from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel

Importance = Literal["HIGH", "MEDIUM", "LOW", "NONE"]


class Period(BaseModel):
    start_date: date
    end_date: date


class Overview(BaseModel):
    period: Period
    total_changes: int
    need_review_count: int  # ai_importance >= min_importance 인 건수
    safety_changes: int
    chemical_changes: int
    environment_changes: int


class DomainLawItem(BaseModel):
    law_id: str
    law_name: str
    change_count: int


class DomainSummaryItem(BaseModel):
    domain: str          # SAFETY / CHEMICAL / ENVIRONMENT
    domain_name: str     # 한글 라벨
    total_changes: int
    laws: List[DomainLawItem]


class DomainSummary(BaseModel):
    domains: List[DomainSummaryItem]


class RecentImportantChangeItem(BaseModel):
    change_id: str
    law_id: str
    law_name: str
    importance: Importance
    change_date: date           # 표시용: 시행일/공포일/수집일 중 하나
    change_type: Optional[str]  # 제개정구분명
    summary: Optional[str]      # change_summary


class RecentImportantChanges(BaseModel):
    items: List[RecentImportantChangeItem]


class ActionItem(BaseModel):
    change_id: str
    law_name: str
    importance: Importance
    action_title: str
    action_detail: str


class ActionItems(BaseModel):
    items: List[ActionItem]


class DashboardResponse(BaseModel):
    overview: Overview
    domain_summary: DomainSummary
    recent_important_changes: RecentImportantChanges
    action_items: ActionItems
