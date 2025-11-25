# app/services/run_daily_admin_rule.py
from datetime import date, timedelta

from app.db.session import SessionLocal
from app.services.nlic_admin_rule_loader import load_admin_rules_for_period


def run_recent_period(days: int = 7) -> None:
    """
    매일 실행한다고 가정:
    - 어제까지 최근 N일치 발령분을 기간으로 수집
    - 중복(admrul_sn)은 DB에서 자동 스킵
    """
    today = date.today()
    end_date = today - timedelta(days=1)
    start_date = end_date - timedelta(days=days - 1)

    db = SessionLocal()
    try:
        summary = load_admin_rules_for_period(
            db=db,
            start_date=start_date,
            end_date=end_date,
            display=100,
        )
        print("[ADMIN_RULE BATCH] summary:", summary)
    finally:
        db.close()


if __name__ == "__main__":
    run_recent_period(days=7)
