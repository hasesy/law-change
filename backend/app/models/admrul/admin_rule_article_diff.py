from sqlalchemy import (
    Column,
    Text,
    DateTime,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from app.db.base import Base


class AdminRuleArticleDiff(Base):
    __tablename__ = "admin_rule_article_diff"

    diff_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # 👉 어떤 변경(신·구 쌍)에 대한 diff인지: AdminRuleOldNewInfo.admrul_sn 와 동일
    admrul_sn = Column(Text, nullable=False)

    old_no = Column(Text, nullable=True)
    old_content = Column(Text, nullable=True)
    new_no = Column(Text, nullable=True)
    new_content = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


Index("idx_admin_rule_article_diff_admrul_sn", AdminRuleArticleDiff.admrul_sn)
