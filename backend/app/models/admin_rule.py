from sqlalchemy import (
    Column,
    Integer,
    Text,
    Date,
    ForeignKey,
    TIMESTAMP,
    func,
    JSON,
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

    admrul_id = Column(Integer, primary_key=True, index=True)
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


class AdminRuleList(Base):
    """
    행정규칙 목록 / 버전 (public.admin_rule_list)
    """
    __tablename__ = "admin_rule_list"
    __allow_unmapped__ = True

    admrul_sn = Column(Text, primary_key=True, index=True)
    admrul_id = Column(
        Integer,
        ForeignKey("admin_rule.admrul_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    admrul_name = Column(Text, nullable=False)
    admrul_type_name = Column(Text, nullable=True)
    ministry_names = Column(Text, nullable=True)

    current_history_type = Column(Text, nullable=True)
    change_type_code = Column(Text, nullable=True)
    change_type_name = Column(Text, nullable=True)

    issue_date = Column(Date, nullable=True)
    enforce_date = Column(Date, nullable=True)
    nlic_registered_date = Column(Date, nullable=True)

    issue_number = Column(Text, nullable=True)
    detail_link_path = Column(Text, nullable=True)

    raw_json = Column(JSON, nullable=True)

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

    admin_rule = relationship(
        "AdminRule",
        back_populates="versions",
    )
