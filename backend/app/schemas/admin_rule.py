# app/schemas/admin_rule.py
from datetime import date
from typing import List, Optional

from pydantic import BaseModel
from app.enums.admin_rule_category import AdminRuleCategory


class AdminRuleListItem(BaseModel):
    admrul_sn: str
    admrul_id: int
    admrul_name: str
    admrul_type_name: Optional[str] = None
    ministry_names: Optional[str] = None

    category: AdminRuleCategory

    issue_date: Optional[date] = None
    enforce_date: Optional[date] = None
    nlic_registered_date: Optional[date] = None

    issue_number: Optional[str] = None

    detail_link_path: Optional[str]


class AdminRuleListResponse(BaseModel):
    total: int
    items: List[AdminRuleListItem]
