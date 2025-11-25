from sqlalchemy import (
    Column, Text, DateTime, func, Enum as SAEnum
)
from sqlalchemy.sql import func
from app.db.base import Base
from app.enums.admin_rule_category import AdminRuleCategory


class Law(Base):
    __tablename__ = "law"

    # law_id TEXT PRIMARY KEY
    law_id = Column(Text, primary_key=True, index=True)
    law_name = Column(Text, nullable=False)
    law_type_name = Column(Text, nullable=True)
    ministry_names = Column(Text, nullable=True)
    ministry_codes = Column(Text, nullable=True)
    category = Column(
        SAEnum(AdminRuleCategory, name="admin_rule_category"),
        nullable=False,
        default=AdminRuleCategory.ETC,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
