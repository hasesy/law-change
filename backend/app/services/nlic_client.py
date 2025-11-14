# app/services/nlic_client.py
from datetime import date
from typing import Any, Dict, List, Tuple
import time

import requests
from requests.exceptions import ReadTimeout, ConnectionError as RequestsConnectionError

from app.core.config import get_settings

settings = get_settings()


class NlicClientError(Exception):
    pass


def _request_json(
    url: str,
    params: Dict[str, Any],
    timeout: int = 230,    # 기본 타임아웃 넉넉하게
    max_retries: int = 5, # 5번까지 재시도
    backoff_sec: float = 1.0,
) -> Dict[str, Any]:
    """
    NLIC 공통 요청 함수
    - 타임아웃/네트워크 에러 시 여러 번 재시도
    - 그래도 안 되면 NlicClientError를 던져서 배치 전체를 중단시킨다 (초기 적재용 strict 모드).
    """
    last_exc: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except (ReadTimeout, RequestsConnectionError) as e:
            last_exc = e
            print(
                f"[NLIC] timeout/conn error (attempt {attempt}/{max_retries}) "
                f"url={url} params={params} err={e}"
            )
            if attempt < max_retries:
                time.sleep(backoff_sec * attempt)  # 1, 2, 3, 4... 초 기다렸다 재시도
            continue
        except Exception as e:
            # HTTP 500, JSON 파싱 오류 등
            raise NlicClientError(f"Request failed: {e}") from e

    # max_retries 다 써도 안 되면 여기로
    raise NlicClientError(
        f"Request to {url} failed after {max_retries} retries: {last_exc}"
    )


def fetch_law_history_page_by_regdt(
    reg_dt: date,
    page: int = 1,
    display: int = 100,
) -> Tuple[List[Dict[str, Any]], bool]:

    reg_dt_str = reg_dt.strftime("%Y%m%d")

    params = {
      "OC": settings.nlic_oc,
      "target": "lsHstInf",
      "type": "JSON",
      "regDt": reg_dt_str,
      "page": page,
      "display": display,
    }

    data = _request_json(settings.nlic_history_url, params)

    service = data.get("LawSearch") or data

    raw_items = service.get("law") or []

    # ✅ 여기서 dict / list 구분해서 항상 list[dict]로 맞춰줌
    if isinstance(raw_items, dict):
        items: List[Dict[str, Any]] = [raw_items]
    elif isinstance(raw_items, list):
        items = raw_items
    else:
        # 혹시나 string이나 이상한 타입 오면 그냥 빈 리스트 처리
        items = []

    total_cnt = int(service.get("totalCnt", len(items)))
    display_ret = int(service.get("display", display))
    page_ret = int(service.get("page", page))

    max_page = (total_cnt + display_ret - 1) // display_ret
    has_next = page_ret < max_page

    return items, has_next


def fetch_old_new(mst: str) -> Dict[str, Any]:
    params = {
        "OC": settings.nlic_oc,
        "target": "oldAndNew",
        "type": "JSON",
        "MST": mst,
    }
    # 내용이 길어서 timeout을 더 줌
    return _request_json(
        settings.nlic_oldnew_url,
        params,
        timeout=230,      # 한 건당 최대 60초까지 기다려 줌
        max_retries=5,   # 60초 * 5번 → 진짜 안 되면 그때 실패
        backoff_sec=2.0,
    )