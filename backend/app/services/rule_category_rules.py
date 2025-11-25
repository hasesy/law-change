from app.enums.admin_rule_category import AdminRuleCategory

# 1) ID 기반 확정 매핑
HARDCODED_CATEGORY_BY_ID: dict[str, AdminRuleCategory] = {
    "46719": AdminRuleCategory.CHEMICAL,
    "93578": AdminRuleCategory.CHEMICAL,
    "46694": AdminRuleCategory.CHEMICAL,
    "46696": AdminRuleCategory.CHEMICAL,
    "68776" : AdminRuleCategory.CHEMICAL,
    "22331": AdminRuleCategory.PSM,
    "29272": AdminRuleCategory.DANGER,
    "27269": AdminRuleCategory.DANGER,
    "22237": AdminRuleCategory.HEALTH,
    "22235": AdminRuleCategory.HEALTH,
    "2047587": AdminRuleCategory.ENV,
    "22232": AdminRuleCategory.HEALTH,
    "2118991" : AdminRuleCategory.HEALTH,
    "2036658": AdminRuleCategory.HEALTH,
    "84684": AdminRuleCategory.FIRE,
}

# 2) 키워드 기반 룰
KEYWORD_RULES: list[tuple[str, AdminRuleCategory]] = [
    ("유해화학물질", AdminRuleCategory.CHEMICAL),

    ("공정안전보고서", AdminRuleCategory.PSM),
    ("산업안전보건", AdminRuleCategory.PSM),

    ("위험물", AdminRuleCategory.DANGER),

    ("노출기준", AdminRuleCategory.HEALTH),
    ("작업환경측정", AdminRuleCategory.HEALTH),
    ("작업환경", AdminRuleCategory.HEALTH),

    ("배출허용기준", AdminRuleCategory.ENV),
    ("배출계수", AdminRuleCategory.ENV),
    ("수질오염물질", AdminRuleCategory.ENV),
    ("대기오염물질", AdminRuleCategory.ENV),
    ("폐기물", AdminRuleCategory.ENV),
    ("폐기물 보관시설", AdminRuleCategory.ENV),

    ("특수건강진단", AdminRuleCategory.HEALTH),
    ("보호구 안전인증", AdminRuleCategory.HEALTH),

    ("소방시설", AdminRuleCategory.FIRE),
    ("소방관리", AdminRuleCategory.FIRE),
    ("피난·대피시설", AdminRuleCategory.FIRE),
    ("소방", AdminRuleCategory.FIRE),
]
