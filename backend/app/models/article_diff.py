from sqlalchemy import (
    Column,
    Text,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from app.db.base import Base


class ArticleDiff(Base):
    __tablename__ = "article_diff"

    diff_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

     # 🔹 이제 mst로만 연결 (change_id 제거)
    mst = Column(Text, nullable=False)

    old_no = Column(Text, nullable=True)
    old_content = Column(Text, nullable=True)
    new_no = Column(Text, nullable=True)
    new_content = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


Index("idx_article_diff_mst", ArticleDiff.mst)
