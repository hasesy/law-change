from app.enums.admin_rule_category import AdminRuleCategory
from app.services.rule_category_rules import HARDCODED_CATEGORY_BY_ID, KEYWORD_RULES

def classify_admin_rule(admin_rule_id: str | None, title: str) -> AdminRuleCategory:
    # 1) ID로 확정된 것
    if admin_rule_id and admin_rule_id in HARDCODED_CATEGORY_BY_ID:
        return HARDCODED_CATEGORY_BY_ID[admin_rule_id]

    # 2) 제목 기반 키워드 매칭
    normalized = (title or "").replace(" ", "")

    for keyword, category in KEYWORD_RULES:
        if keyword.replace(" ", "") in normalized:
            return category

    # 3) 둘 다 없으면 ‘기타’
    return AdminRuleCategory.ETC
