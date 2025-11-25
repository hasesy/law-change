# app/services/law_category_backfill.py

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.law.law import Law
from app.enums.admin_rule_category import AdminRuleCategory
from app.services.categorizer import classify_law


def backfill_law_categories(
    db: Session,
    overwrite_etc: bool = False,
) -> int:
    """
    law 테이블 전체를 훑으면서 category가 비어 있는 row(또는 ETC만)들을
    classify_law로 채워 넣는다.

    :param overwrite_etc: True면 기존에 ETC로 들어있는 것도 다시 분류해서 덮어씀
    :return: 업데이트된 row 개수
    """

    stmt = select(Law)

    if not overwrite_etc:
        # category IS NULL 인 것만
        stmt = stmt.where(Law.category.is_(None))
    else:
        # NULL + ETC 모두 다시 채우고 싶으면
        stmt = stmt.where(
            (Law.category.is_(None)) | (Law.category == AdminRuleCategory.ETC)
        )

    result = db.execute(stmt)
    laws = result.scalars().all()

    updated = 0
    for law in laws:
        if not law.law_name:
            continue

        new_category = classify_law(law_id=law.law_id, law_name=law.law_name)
        if law.category != new_category:
            law.category = new_category
            updated += 1

    db.commit()
    return updated
