from sqlalchemy import (
    Column,
    Text,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

from app.db.base import Base


class LawChangeEvent(Base):
    __tablename__ = "law_change_event"

    # change_id UUID PRIMARY KEY DEFAULT gen_random_uuid()
    change_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    law_id = Column(
        Text,
        ForeignKey("law.law_id", ondelete="CASCADE"),
        nullable=False,
    )

    mst = Column(Text, nullable=False)  # 법령일련번호
    change_type = Column(Text, nullable=True)  # 제개정구분명
    proclamation_no = Column(Text, nullable=True)
    proclamation_date = Column(Date, nullable=True)
    enforce_date = Column(Date, nullable=True)
    current_hist_cd = Column(Text, nullable=True)
    collected_date = Column(Date, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # UNIQUE (law_id, mst)
    __table_args__ = (
        # SQLAlchemy 2.x 방식
        # UniqueConstraint("law_id", "mst", name="uq_law_change_event_law_mst"),
    )

    law = relationship("Law", backref="change_events")

__table_args__ = (
    UniqueConstraint("law_id", "mst", name="uq_law_change_event_law_mst"),
)