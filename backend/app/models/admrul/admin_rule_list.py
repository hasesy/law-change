from sqlalchemy import (
    Column,
    Integer,
    Text,
    Date,
    ForeignKey,
    TIMESTAMP,
    func,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.base import Base

class AdminRuleList(Base):
    """
    행정규칙 목록 / 버전 (public.admin_rule_list)
    """
    __tablename__ = "admin_rule_list"
    __allow_unmapped__ = True

    admrul_sn = Column(Text, primary_key=True, index=True)
    admrul_id = Column(
        Text,
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
    
    change_summary = Column(Text, nullable=True)           # 내용요약
    action_recommendation = Column(Text, nullable=True)     # 조치사항
    ai_importance = Column(Text, nullable=True)  # 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE'

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