# app/schemas/law_change.py
from datetime import date
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class LawChangeListItem(BaseModel):
    change_id: UUID
    law_id: str
    law_name: str
    law_type_name: Optional[str] = None
    ministry_names: Optional[str] = None

    change_type: Optional[str] = None
    proclamation_no: Optional[str] = None
    proclamation_date: Optional[date] = None
    enforce_date: Optional[date] = None
    current_hist_cd: Optional[str] = None
    collected_date: date
    change_summary: Optional[str] = None
    action_recommendation: Optional[str] = None

    class Config:
        orm_mode = True


class LawChangeListResponse(BaseModel):
    total: int
    items: List[LawChangeListItem]


class ArticleDiffItem(BaseModel):
    diff_id: UUID
    old_no: Optional[str] = None
    old_content: Optional[str] = None
    new_no: Optional[str] = None
    new_content: Optional[str] = None

    class Config:
        from_attributes = True 


class LawChangeSummary(BaseModel):
    change_id: UUID
    law_id: str
    law_name: str
    law_type_name: Optional[str] = None
    ministry_names: Optional[str] = None
    change_type: Optional[str] = None
    proclamation_no: Optional[str] = None
    proclamation_date: Optional[date] = None
    enforce_date: Optional[date] = None
    collected_date: date
    change_summary: Optional[str] = None
    action_recommendation: Optional[str] = None

    class Config:
        orm_mode = True


class LawChangeDetail(BaseModel):
    change: LawChangeSummary
    has_old_new: str              # 'Y' / 'N'
    old_basic: Optional[Dict[str, Any]] = None
    new_basic: Optional[Dict[str, Any]] = None
    articles: List[ArticleDiffItem]

    class Config:
        orm_mode = True
