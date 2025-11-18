import time

from app.db.session import SessionLocal
from app.services.ai_summarizer import generate_ai_for_pending_changes


def main():
    db = SessionLocal()
    try:
        start = time.perf_counter()
        count = generate_ai_for_pending_changes(db, limit=10)
        elapsed = time.perf_counter() - start
        
        print(f"AI 요약 생성 완료 → {count}건 처리됨")
        if count > 0:
            print(f"총 소요 시간: {elapsed:.2f}초 (건당 평균 {elapsed / count:.2f}초)")
        else:
            print(f"총 소요 시간: {elapsed:.2f}초 (처리 건수 0건)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
