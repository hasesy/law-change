# app/services/run_backfill_law_category.py

from app.db.session import SessionLocal
from app.services.law_category_backfill import backfill_law_categories

# 나중에 카테고리 룰 추가 시 overwrite_etc=True로 돌리기 (카테고리 '기타'인 것만 재분류)
def run():
    db = SessionLocal()
    try:
        updated = backfill_law_categories(db, overwrite_etc=False)
        print(f"[law category backfill] updated rows = {updated}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
