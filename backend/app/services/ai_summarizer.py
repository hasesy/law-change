# app/services/ai_summarizer.py

import json
import logging
from typing import Optional, Tuple
import time
import re
import html

import requests
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import get_settings
from app.models.law_change_event import LawChangeEvent
from app.models.law import Law
from app.models.law_old_new_info import LawOldNewInfo
from app.models.law_article_diff import LawArticleDiff

logger = logging.getLogger(__name__)

settings = get_settings()
OLLAMA_URL = f"{settings.ollama_base_url}/api/generate"
OLLAMA_MODEL = settings.ollama_model_name


def _clean_html(text: str) -> str:
    """old_content/new_content 안의 <p> 같은 단순 강조태그 제거만."""
    if not text:
        return ""

    text = html.unescape(text)

    # <p> 또는 </p> 제거만 수행
    text = re.sub(r"</?p\s*>", "", text, flags=re.IGNORECASE)

    return text.strip()

def _format_basic_json(basic: dict | None, label: str) -> str:
    """old_basic / new_basic JSONB를 사람이 읽기 좋게 정리."""
    if not isinstance(basic, dict):
        return f"[{label}] 정보 없음"

    lines: list[str] = []
    for key, value in basic.items():
        if value is None or value == "":
            continue
        s = str(value)
        lines.append(f"- {key}: {s}")

    if not lines:
        return f"[{label}] 정보 없음"

    return f"[{label}]\n" + "\n".join(lines)


def _format_article_diffs(rows: list[LawArticleDiff], max_rows: int = 5) -> str:
    """ArticleDiff 여러 건을 조문별 변경 요약 형태로 정리."""
    if not rows:
        return "조문별 diff 정보 없음"

    lines: list[str] = []
    for idx, row in enumerate(rows[:max_rows], start=1):
        old_no = (row.old_no or "").strip()
        new_no = (row.new_no or "").strip()
        no_display = old_no or new_no or "(조문 번호 없음)"

        old_text = _clean_html(row.old_content or "")
        new_text = _clean_html(row.new_content or "")

        lines.append(
            f"- 조문 {no_display} (항목 {idx})\n"
            f"  [개정 전]\n  {old_text or '(내용 없음)'}\n"
            f"  [개정 후]\n  {new_text or '(내용 없음)'}"
        )

    if len(rows) > max_rows:
        lines.append(f"... (총 {len(rows)}개 중 상위 {max_rows}개만 표시)")

    return "\n".join(lines)

def build_prompt_for_change(db: Session, change: LawChangeEvent) -> str:
    """법령 변경이력 1건에 대해 Qwen에게 줄 프롬프트 생성 (mst 기준 old/new + diff 포함)."""

    law: Optional[Law] = change.law

    law_name = getattr(law, "law_name", "") if law else ""
    law_type_name = getattr(law, "law_type_name", "") if law else ""
    ministry_names = getattr(law, "ministry_names", "") if law else ""

    meta_part = f"""
                법령명: {law_name}
                법령유형: {law_type_name}
                소관부처: {ministry_names}
                제개정구분: {change.change_type or ""}
                공포번호: {change.proclamation_no or ""}
                공포일: {change.proclamation_date or ""}
                시행일: {change.enforce_date or ""}
                수집일: {change.collected_date or ""}
                MST: {change.mst}
                """

    # 🔹 mst 기준으로 OldNewInfo 1건 (있으면)
    old_new: LawOldNewInfo | None = (
        db.query(LawOldNewInfo)
        .filter(
            LawOldNewInfo.mst == change.mst,
            LawOldNewInfo.has_old_new == "Y",
        )
        .one_or_none()
    )

    if old_new:
        old_basic_text = _format_basic_json(old_new.old_basic, "개정 전 기본 정보")
        new_basic_text = _format_basic_json(old_new.new_basic, "개정 후 기본 정보")
        old_new_text = f"{old_basic_text}\n\n{new_basic_text}"
    else:
        old_new_text = "신·구조문 기본 정보 없음 (has_old_new != 'Y')"

    # 🔹 mst 기준 ArticleDiff 여러 건
    diff_rows = (
        db.query(LawArticleDiff)
        .filter(LawArticleDiff.mst == change.mst)
        .all()
    )
    diff_text = _format_article_diffs(diff_rows, max_rows=5)

    detail_part = f"""
                [신·구조문 정보 요약]
                {old_new_text}

                [조문별 diff 정보 요약]
                {diff_text}
                """

    prompt = f"""
            당신은 한국 산업안전보건·환경 법규를 분석하는 컴플라이언스 전문가입니다.
            아래 정보는 안전보건관리 솔루션(중대재해처벌법 대응, KOSHA 가이드 기반)의
            법규 변경이력입니다.

            이 솔루션의 주요 메뉴는 다음과 같습니다.
            - 경영: 경영책임자 의무, 안전보건 방침/목표, 이사회 보고 등
            - 안전관리: 위험성평가, 작업허가, 설비/시설 점검, 법규 준수 평가, 자체점검
            - 보건: 근로자 건강검진, 작업환경측정, 보호구 관리, 직업병 예방
            - 환경: 대기/수질/폐기물/화학물질 관리, 배출시설 인허가, 환경점검

            사용자는 공장 현장 근로자, 안전관리자, 환경/보건 담당자입니다.

            [변경 이력 메타 정보]
            {meta_part}

            [신·구조문 및 diff 정보]
            {detail_part}

            요청사항:
            1. 이번 법령 변경의 중요도를 아래 중 하나로 판단해 주세요.
            - NONE: 시스템 관점에서 별도 조치가 거의 필요 없는 경미한 변경
            - LOW: 인지는 필요하지만 즉시적인 조치는 크지 않은 변경
            - MEDIUM: 관련 메뉴/문서를 수정해야 할 가능성이 있는 변경
            - HIGH: 반드시 조치해야 하는 중요한 변경

            2. 현업 담당자가 이해하기 쉽게, 변경의 핵심 내용을 한국어로 3~5줄 정도로 요약해 주세요.
            - 실제로 변경된 조문(신·구조문 / diff)을 중심으로 설명해 주세요.

            3. 우리 솔루션을 사용하는 사용자가 해야 할 구체적인 조치사항을 제안해 주세요.
            - 담당자 관점으로 작성: 예) "안전관리자", "현장 반장", "환경 담당자", "경영책임자" 등
            - 솔루션 메뉴와 연결해서 작성: 위험성평가, 법규 준수 평가, 작업허가, 교육관리, 문서관리, 설비점검, 환경점검 등
            - 체크리스트 형태의 액션으로 작성: "무엇을, 어느 메뉴에서, 어떻게 변경/추가/점검할지"를 써주세요.

            4. 만약 시스템이나 현장 조치가 사실상 필요 없는 경미한 변경이라면,
            - importance를 "NONE"으로 설정하고
            - actions 배열에는 "조치할 사항이 없습니다." 한 줄만 넣어 주세요.

            반드시 아래 JSON 형식으로만 출력하세요. 다른 문장/설명은 절대 쓰지 마세요.

            {{
            "importance": "HIGH | MEDIUM | LOW | NONE 중 하나",
            "summary": "변경 내용을 한국어로 요약",
            "actions": [
                "첫번째 조치사항",
                "두번째 조치사항"
            ]
            }}
            """
    return prompt.strip()


def call_ollama(prompt: str, max_retries: int = 2) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    last_error = None
    for attempt in range(1, max_retries + 1):
        start = time.perf_counter()
        resp = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        raw = (data.get("response") or "").strip()
        elapsed = time.perf_counter() - start

        logger.info(f"[AI] Ollama 호출 시간: {elapsed:.2f}초 (attempt={attempt})")
        print(f"[AI] Ollama 호출 시간: {elapsed:.2f}초 (attempt={attempt})")

        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            last_error = e
            logger.warning(
                "AI JSON 파싱 실패 (attempt=%d). raw 일부: %s",
                attempt, raw[:200],
            )
            if attempt == max_retries:
                return None, None, None
            # 약간의 딜레이 후 재시도
            time.sleep(1)
            continue

        # 여기서부터는 성공한 경우
        importance = (obj.get("importance") or "").strip().upper() or None
        summary = obj.get("summary") or ""
        actions = obj.get("actions") or []

        if importance == "NONE":
            actions = ["조치할 사항이 없습니다."]

        if isinstance(actions, list):
            actions_text = "\n".join(f"- {a}" for a in actions)
        elif isinstance(actions, str):
            actions_text = actions
        else:
            actions_text = None

        return summary, actions_text, importance

    # 여기까지 오면 전부 실패
    logger.error("AI 호출/파싱이 모두 실패했습니다: %s", last_error)
    return None, None, None


def generate_ai_for_pending_changes(db: Session, limit: int = 10) -> int:
    """
    아직 요약/조치가 없는 변경이력들 중,
    old_new_info.has_old_new = 'Y' 인 mst만 대상으로,
    collected_date 최신순으로 limit 만큼 처리.
    """
    # has_old_new = 'Y'인 mst만 추출
    mst_select = (
        select(LawOldNewInfo.mst)
        .where(LawOldNewInfo.has_old_new == "Y")
    )

    # collected_date DESC 기준으로 최신 10개만
    queryset = (
        db.query(LawChangeEvent)
        .filter(
            LawChangeEvent.mst.in_(mst_select),
            LawChangeEvent.change_summary.is_(None),
            LawChangeEvent.action_recommendation.is_(None),
        )
        .order_by(LawChangeEvent.collected_date.desc(), LawChangeEvent.created_at.desc())
        .limit(limit)
        .all()
    )

    count = 0
    for change in queryset:
        try:
            prompt = build_prompt_for_change(db, change)
            summary, actions, importance = call_ollama(prompt)
            
            # ❗ 파싱 실패한 경우: 이번 change는 건너뛰기
            if summary is None and actions is None and importance is None:
                logger.warning(
                    "AI 응답 파싱 실패로 change_id=%s 는 저장하지 않습니다.",
                    change.change_id,
                )
                # rollback은 안 해도 되지만 혹시 몰라 해도 OK
                db.rollback()
                continue
            
            change.change_summary = summary
            change.action_recommendation = actions
            change.ai_importance = importance
            
            db.add(change)
            db.commit()
            count += 1
        except Exception as e:
            db.rollback()
            logger.exception(f"AI 요약 생성 실패 (change_id={change.change_id}): {e}")

    return count
