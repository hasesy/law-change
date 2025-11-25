# app/schemas/admin_rule.py
from datetime import date
from typing import List, Optional, Literal, Any
from uuid import UUID

from pydantic import BaseModel
from app.enums.admin_rule_category import AdminRuleCategory


class AdminRuleListItem(BaseModel):
    admrul_sn: str
    admrul_id: str
    admrul_name: str
    
    admrul_type_name: Optional[str] = None
    ministry_names: Optional[str] = None
    category: AdminRuleCategory

    change_type_name: Optional[str] = None
    current_history_type: Optional[str] = None
    issue_number: Optional[str] = None
    issue_date: Optional[date] = None
    enforce_date: Optional[date] = None
    nlic_registered_date: Optional[date] = None
    
    change_summary: Optional[str] = None
    action_recommendation: Optional[str] = None
    ai_importance: Optional[str] = None

    detail_link_path: Optional[str]
    
    class Config:
        from_attributes = True


class AdminRuleListResponse(BaseModel):
    total: int
    items: List[AdminRuleListItem]


class AdminRuleSummary(BaseModel):
    """
    상세에서 상단 요약에 쓸 행정규칙 한 건
    - 프론트 LawChangeEvent 구조를 행정규칙 버전으로 맞춘 느낌
    """
    admrul_sn: int
    admrul_id: str
    admrul_name: str

    admrul_type_name: Optional[str] = None
    ministry_names: Optional[str] = None
    category: Optional[AdminRuleCategory] = None
    change_type_name: Optional[str] = None
    current_history_type: Optional[str] = None

    issue_number: Optional[str] = None
    issue_date: Optional[date] = None
    enforce_date: Optional[date] = None
    nlic_registered_date: Optional[date] = None

    change_summary: Optional[str] = None
    action_recommendation: Optional[str] = None
    ai_importance: Optional[str] = None

    class Config:
        from_attributes = True


class AdminRuleArticleDiffItem(BaseModel):
    """
    행정규칙 조문 비교 1건
    (법령쪽 ArticleDiffItem과 동일 구조)
    """
    diff_id: UUID
    old_no: Optional[str] = None
    old_content: Optional[str] = None
    new_no: Optional[str] = None
    new_content: Optional[str] = None

    class Config:
        from_attributes = True


class AdminRuleChangeDetail(BaseModel):
    """
    행정규칙 상세 + 신·구법 + 조문비교

    {
      rule:      AdminRuleSummary,
      has_old_new: "Y" | "N",
      old_basic: {...} | null,
      new_basic: {...} | null,
      articles:  AdminRuleArticleDiffItem[]
    }
    """
    rule: AdminRuleSummary
    has_old_new: Literal["Y", "N"]
    old_basic: Optional[dict[str, Any]] = None
    new_basic: Optional[dict[str, Any]] = None
    articles: List[AdminRuleArticleDiffItem] = []
    
    class Config:
        from_attributes = True