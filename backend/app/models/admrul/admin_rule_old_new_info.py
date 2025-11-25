from sqlalchemy import (
    Column,
    Text,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base import Base


class AdminRuleOldNewInfo(Base):
    __tablename__ = "admin_rule_old_new_info"

    # 👉 기준 키: "신조문"의 행정규칙일련번호(admrul_sn)를 PK로 사용
    admrul_sn = Column(
        Text,
        primary_key=True,
        comment="신조문 행정규칙일련번호 (law에서 mst 역할)",
    )

    # 옵션: master / list와 FK를 묶고 싶으면 이렇게
    # admrul_sn = Column(
    #     Text,
    #     ForeignKey("admin_rule_list.admrul_sn", ondelete="CASCADE"),
    #     primary_key=True,
    # )

    has_old_new = Column(Text, nullable=False)  # 'Y' or 'N'
    # DRF AdmRulOldAndNewService 의 구조문_기본정보 전체 JSON
    old_basic = Column(JSONB, nullable=False)
    # DRF AdmRulOldAndNewService 의 신조문_기본정보 전체 JSON
    new_basic = Column(JSONB, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "has_old_new IN ('Y','N')",
            name="ck_admin_rule_old_new_info_has_old_new",
        ),
    )
