from sqlalchemy import (
    Column,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.db.base import Base


class OldNewInfo(Base):
    __tablename__ = "old_new_info"

    mst = Column(Text, primary_key=True)

    has_old_new = Column(Text, nullable=False)  # 'Y' or 'N'
    old_basic = Column(JSONB, nullable=False)
    new_basic = Column(JSONB, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("has_old_new IN ('Y','N')", name="ck_old_new_info_has_old_new"),
    )
