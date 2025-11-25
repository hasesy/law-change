# app/services/dashboard_service.py
from datetime import date, timedelta
from typing import Dict, List, Tuple

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.law import Law
from app.models.law_change_event import LawChangeEvent
from app.schemas.dashboard import (
    DashboardResponse,
    Overview,
    Period,
    DomainSummary,
    DomainSummaryItem,
    DomainLawItem,
    RecentImportantChanges,
    RecentImportantChangeItem,
    ActionItems,
    ActionItem,
    Importance,
)

# 중요도 순서 (낮 -> 높)
IMPORTANCE_ORDER = ["NONE", "LOW", "MEDIUM", "HIGH"]

# 대시보드에 고정으로 쓸 3개 도메인 + 9개 법령
DASHBOARD_LAW_GROUPS: Dict[str, Dict] = {
    "SAFETY": {
        "domain_name": "안전",
        "law_ids": ["001766", "013993", "009503"],  # 산안법, 중대재해, 소방시설
    },
    "CHEMICAL": {
        "domain_name": "화학",
        "law_ids": ["000162", "011857", "009502"],  # 화관법, 화평법, 위험물안전
    },
    "ENVIRONMENT": {
        "domain_name": "환경",
        "law_ids": ["001773", "000166", "001771"],  # 대기, 물환경, 폐기물
    },
}


def _calc_period(days: int) -> Period:
    """collected_date 기준 기간 계산 (오늘 포함)"""
    today = date.today()
    start = today - timedelta(days=days - 1)
    return Period(start_date=start, end_date=today)


def _importance_rank_case():
    """ai_importance 정렬용 case expression"""
    return case(
        (LawChangeEvent.ai_importance == "HIGH", 3),
        (LawChangeEvent.ai_importance == "MEDIUM", 2),
        (LawChangeEvent.ai_importance == "LOW", 1),
        else_=0,
    ).label("importance_rank")


def _importance_filter_values(min_importance: Importance) -> List[str]:
    """min_importance 이상인 ai_importance 값 리스트"""
    min_idx = IMPORTANCE_ORDER.index(min_importance)
    return IMPORTANCE_ORDER[min_idx:]


def get_dashboard(
    db: Session,
    days: int = 7,
    min_importance: Importance = "MEDIUM",
    action_limit: int = 5,
) -> DashboardResponse:
    period = _calc_period(days)

    # -------------------------------------------------
    # 공통 base 쿼리: collected_date 기간 필터
    # -------------------------------------------------
    base_q = (
        db.query(LawChangeEvent)
        .filter(LawChangeEvent.collected_date >= period.start_date)
        .filter(LawChangeEvent.collected_date <= period.end_date)
    )

    # =========================
    # 1) Overview
    # =========================
    total_changes = base_q.count()

    # '검토 필요'는 일단 ai_importance >= min_importance 로 정의
    importance_values = _importance_filter_values(min_importance)
    need_review_count = (
        base_q.filter(LawChangeEvent.ai_importance.in_(importance_values)).count()
    )

    # 도메인별 건수는 아래 DomainSummary 계산을 재사용하기 위해
    # 먼저 law_id별 change_count를 한 번에 구해둔다.
    # {law_id: count}
    law_counts_rows: List[Tuple[str, int]] = (
        db.query(
            LawChangeEvent.law_id,
            func.count(LawChangeEvent.change_id).label("cnt"),
        )
        .filter(
            LawChangeEvent.collected_date >= period.start_date,
            LawChangeEvent.collected_date <= period.end_date,
        )
        .group_by(LawChangeEvent.law_id)
        .all()
    )
    law_count_map: Dict[str, int] = {law_id: cnt for law_id, cnt in law_counts_rows}

    # 도메인별 총합 (나중에 Overview + DomainSummary 둘 다 사용)
    domain_total_map: Dict[str, int] = {"SAFETY": 0, "CHEMICAL": 0, "ENVIRONMENT": 0}
    for domain_key, info in DASHBOARD_LAW_GROUPS.items():
        total = 0
        for law_id in info["law_ids"]:
            total += law_count_map.get(law_id, 0)
        domain_total_map[domain_key] = total

    overview = Overview(
        period=period,
        total_changes=total_changes,
        need_review_count=need_review_count,
        safety_changes=domain_total_map["SAFETY"],
        chemical_changes=domain_total_map["CHEMICAL"],
        environment_changes=domain_total_map["ENVIRONMENT"],
    )

    # =========================
    # 2) Domain summary
    # =========================
    # 9개 고정 law_id 에 대한 law_name 을 한 번에 가져온다.
    all_law_ids: List[str] = sum(
        [info["law_ids"] for info in DASHBOARD_LAW_GROUPS.values()], []
    )

    law_name_rows = (
        db.query(Law.law_id, Law.law_name)
        .filter(Law.law_id.in_(all_law_ids))
        .all()
    )
    law_name_map: Dict[str, str] = {law_id: name for law_id, name in law_name_rows}

    domain_items: List[DomainSummaryItem] = []
    for domain_key, info in DASHBOARD_LAW_GROUPS.items():
        laws: List[DomainLawItem] = []
        total_changes_domain = 0
        for law_id in info["law_ids"]:
            cnt = law_count_map.get(law_id, 0)
            total_changes_domain += cnt
            law_name = law_name_map.get(law_id, law_id)
            laws.append(
                DomainLawItem(
                    law_id=law_id,
                    law_name=law_name,
                    change_count=cnt,
                )
            )

        domain_items.append(
            DomainSummaryItem(
                domain=domain_key,
                domain_name=info["domain_name"],
                total_changes=total_changes_domain,
                laws=laws,
            )
        )

    domain_summary = DomainSummary(domains=domain_items)

    # =========================
    # 3) 최근 중요 변경 이력 리스트
    # =========================
    importance_rank = _importance_rank_case()

    recent_rows = (
        db.query(
            LawChangeEvent,
            Law,
            importance_rank,
        )
        .join(Law, Law.law_id == LawChangeEvent.law_id)
        .filter(LawChangeEvent.collected_date >= period.start_date)
        .filter(LawChangeEvent.collected_date <= period.end_date)
        .filter(LawChangeEvent.ai_importance.in_(importance_values))
        .order_by(importance_rank.desc(), LawChangeEvent.collected_date.desc())
        .limit(20)
        .all()
    )

    recent_items: List[RecentImportantChangeItem] = []
    for event, law, _rank in recent_rows:
        # 표시용 날짜: 시행일 > 공포일 > 수집일
        change_date = (
            event.enforce_date
            or event.proclamation_date
            or event.collected_date
        )

        recent_items.append(
            RecentImportantChangeItem(
                change_id=str(event.change_id),
                law_id=law.law_id,
                law_name=law.law_name,
                importance=(event.ai_importance or "NONE"),  # NULL 방어
                change_date=change_date,
                change_type=event.change_type,
                summary=event.change_summary,
            )
        )

    recent_important_changes = RecentImportantChanges(items=recent_items)

    # =========================
    # 4) 주요 조치사항
    # =========================
    action_rows = (
        db.query(LawChangeEvent, Law, importance_rank)
        .join(Law, Law.law_id == LawChangeEvent.law_id)
        .filter(LawChangeEvent.collected_date >= period.start_date)
        .filter(LawChangeEvent.collected_date <= period.end_date)
        .filter(LawChangeEvent.ai_importance.in_(importance_values))
        .filter(LawChangeEvent.action_recommendation.isnot(None))
        .order_by(importance_rank.desc(), LawChangeEvent.collected_date.desc())
        .all()
    )

    action_items: List[ActionItem] = []

    def make_title_from_text(text: str) -> str:
        """조치사항 텍스트에서 한 줄 제목 뽑기 (간단 버전)"""
        if not text:
            return ""
        # 줄바꿈 기준 첫 줄
        first_line = text.splitlines()[0].strip()
        # 너무 길면 앞 30자만 사용
        if len(first_line) > 30:
            return first_line[:30] + "..."
        return first_line

    for event, law, _rank in action_rows:
        detail = event.action_recommendation
        if not detail:
            continue

        title = make_title_from_text(detail)
        if not title:
            # 제목이 비면 법령명 기반 기본 문구
            title = f"{law.law_name} 관련 조치"

        action_items.append(
            ActionItem(
                change_id=str(event.change_id),
                law_name=law.law_name,
                importance=(event.ai_importance or "NONE"),
                action_title=title,
                action_detail=detail,
            )
        )
        if len(action_items) >= action_limit:
            break

    action_items_model = ActionItems(items=action_items)

    # =========================
    # 최종 조합
    # =========================
    return DashboardResponse(
        overview=overview,
        domain_summary=domain_summary,
        recent_important_changes=recent_important_changes,
        action_items=action_items_model,
    )
