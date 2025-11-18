# app/services/run_daily_nlic.py
from datetime import date, timedelta

from app.db.session import SessionLocal
from app.services.nlic_loader import load_changes_for_date


def run_for_yesterday() -> None:
    yesterday = date.today() - timedelta(days=1)
    db = SessionLocal()
    try:
        summary = load_changes_for_date(db, yesterday)
        print("[NLIC DAILY] done:", summary)
    finally:
        db.close()


if __name__ == "__main__":
    run_for_yesterday()
