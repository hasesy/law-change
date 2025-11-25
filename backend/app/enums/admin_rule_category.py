from enum import Enum

class AdminRuleCategory(str, Enum):
    CHEMICAL = "CHEMICAL"
    PSM = "PSM"
    DANGER = "DANGER"
    ENV = "ENV"
    HEALTH = "HEALTH"
    FIRE = "FIRE"
    ETC = "ETC"
