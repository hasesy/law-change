from app.enums.admin_rule_category import AdminRuleCategory

# 행정규칙 ID 기반 확정 매핑
RULE_HARDCODED_CATEGORY_BY_ID: dict[str, AdminRuleCategory] = {
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
    "22232": AdminRuleCategory.HEALTH,
    "2118991" : AdminRuleCategory.HEALTH,
    "2036658": AdminRuleCategory.HEALTH,
    
    "2047587": AdminRuleCategory.ENV,
    
    "84684": AdminRuleCategory.FIRE,
}

# 법령 ID 기반 확정 매핑
LAW_HARDCODED_CATEGORY_BY_ID: dict[str, AdminRuleCategory] = {
    "001766" : AdminRuleCategory.PSM, # 산업안전보건법
    "003786" : AdminRuleCategory.PSM, # 산업안전보건법 시행령
    "007364" : AdminRuleCategory.PSM, # 산업안전보건법 시행규칙
    "007363" : AdminRuleCategory.PSM, # 산업안전보건기준에 관한 규칙
    "000150" : AdminRuleCategory.PSM, # 한국산업안전보건공단법
    "005443" : AdminRuleCategory.PSM, # 한국산업안전보건공단법 시행령
    
    "009502" : AdminRuleCategory.DANGER, # 위험물안전관리법
    "009707" : AdminRuleCategory.DANGER, # 위험물안전관리법 시행령
    "009732" : AdminRuleCategory.DANGER, # 위험물안전관리법 시행규칙
    "001850" : AdminRuleCategory.DANGER, # 고압가스 안전관리법
    "002246" : AdminRuleCategory.DANGER, # 고압가스 안전관리법 시행령
    "006285" : AdminRuleCategory.DANGER, # 고압가스 안전관리법 시행규칙
    
    "000162" : AdminRuleCategory.CHEMICAL, # 화학물질관리법
    "004390" : AdminRuleCategory.CHEMICAL, # 화학물질관리법 시행령
    "007845" : AdminRuleCategory.CHEMICAL, # 화학물질관리법 시행규칙
    "011857" : AdminRuleCategory.CHEMICAL, # 화학물질 등록 및 평가 등에 관한 법률
    "012183" : AdminRuleCategory.CHEMICAL, # 화학물질 등록 및 평가 등에 관한 법률 시행령
    "012201" : AdminRuleCategory.CHEMICAL, # 화학물질 등록 및 평가 등에 관한 법률 시행규칙
    
    "009503" : AdminRuleCategory.FIRE, # 소방시설 설치 및 관리에 관한 법률
    "009694" : AdminRuleCategory.FIRE, # 소방시설 설치 및 관리에 관한 법률 시행령
    "009730" : AdminRuleCategory.FIRE, # 소방시설 설치 및 관리에 관한 법률 시행규칙
    
    "010711" : AdminRuleCategory.ENV, # 환경보건법
    "010923" : AdminRuleCategory.ENV, # 환경보건법 시행령
    "010964" : AdminRuleCategory.ENV, # 환경보건법 시행규칙
    "001773" : AdminRuleCategory.ENV, # 대기환경보전법
    "003302" : AdminRuleCategory.ENV, # 대기환경보전법 시행령
    "007038" : AdminRuleCategory.ENV, # 대기환경보전법 시행규칙
    "000160" : AdminRuleCategory.ENV, # 토양환경보전법
    "005273" : AdminRuleCategory.ENV, # 토양환경보전법 시행령
    "008508" : AdminRuleCategory.ENV, # 토양환경보전법 시행규칙
    "000166" : AdminRuleCategory.ENV, # 물환경보전법
    "004037" : AdminRuleCategory.ENV, # 물환경보전법 시행령
    "007575" : AdminRuleCategory.ENV, # 물환경보전법 시행규칙
    "001771" : AdminRuleCategory.ENV, # 폐기물관리법
    "005353" : AdminRuleCategory.ENV, # 폐기물관리법 시행령
    "008567" : AdminRuleCategory.ENV, # 폐기물관리법 시행규칙
    "010722" : AdminRuleCategory.ENV, # 방사성폐기물 관리법
    "010887" : AdminRuleCategory.ENV, # 방사성폐기물 관리법 시행령
    "010891" : AdminRuleCategory.ENV, # 방사성폐기물 관리법 시행규칙
}

# 공통) 키워드 기반 룰
KEYWORD_RULES: list[tuple[str, AdminRuleCategory]] = [
    ("유해화학물질", AdminRuleCategory.CHEMICAL),

    ("공정안전보고서", AdminRuleCategory.PSM),
    ("산업안전보건", AdminRuleCategory.PSM),

    ("위험물", AdminRuleCategory.DANGER),
    ("고압가스", AdminRuleCategory.DANGER),

    ("노출기준", AdminRuleCategory.HEALTH),
    ("작업환경측정", AdminRuleCategory.HEALTH),
    ("작업환경", AdminRuleCategory.HEALTH),
    ("특수건강진단", AdminRuleCategory.HEALTH),
    ("보호구 안전인증", AdminRuleCategory.HEALTH),

    ("배출허용기준", AdminRuleCategory.ENV),
    ("배출계수", AdminRuleCategory.ENV),
    ("수질오염물질", AdminRuleCategory.ENV),
    ("대기오염물질", AdminRuleCategory.ENV),
    ("폐기물", AdminRuleCategory.ENV),
    ("폐기물 보관시설", AdminRuleCategory.ENV),


    ("소방시설", AdminRuleCategory.FIRE),
    ("소방관리", AdminRuleCategory.FIRE),
    ("피난·대피시설", AdminRuleCategory.FIRE),
    ("소방", AdminRuleCategory.FIRE),
]
