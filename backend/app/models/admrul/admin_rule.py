from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    func,
    Enum as SAEnum
)
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.enums.admin_rule_category import AdminRuleCategory


class AdminRule(Base):
    """
    행정규칙 마스터 (public.admin_rule)
    """
    __tablename__ = "admin_rule"
    __allow_unmapped__ = True  # 타입힌트 없는 구방식 허용

    admrul_id = Column(Text, primary_key=True, index=True)
    admrul_name = Column(Text, nullable=False)
    admrul_type_name = Column(Text, nullable=True)
    ministry_names = Column(Text, nullable=True)
    category = Column(
        SAEnum(AdminRuleCategory, name="admin_rule_category"),
        nullable=False,
        default=AdminRuleCategory.ETC,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # 관계: 한 규칙ID(admrul_id)에 여러 버전(admrul_sn)
    versions = relationship(
        "AdminRuleList",
        back_populates="admin_rule",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )



