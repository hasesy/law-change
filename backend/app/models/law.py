from sqlalchemy import Column, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Law(Base):
    __tablename__ = "law"

    # law_id TEXT PRIMARY KEY
    law_id = Column(Text, primary_key=True, index=True)
    law_name = Column(Text, nullable=False)
    law_type_name = Column(Text, nullable=True)
    ministry_names = Column(Text, nullable=True)
    ministry_codes = Column(Text, nullable=True)

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
