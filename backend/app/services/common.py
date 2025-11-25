# app/services/nlic_common.py
from datetime import datetime, date
from typing import Any, Dict, List, Optional


def parse_ymd(s: Optional[str]) -> Optional[date]:
    """
    'YYYYMMDD' 또는 'YYYY-MM-DD' 형태 문자열을 date로 변환.
    - None / 빈 문자열 / 길이 안 맞으면 None 리턴
    """
    if not s:
        return None
    s = str(s).replace("-", "").strip()
    if len(s) != 8:
        return None
    try:
        return datetime.strptime(s, "%Y%m%d").date()
    except Exception:
        return None


def ensure_list_dict(v: Any) -> List[Dict[str, Any]]:
    """
    dict | list[dict] | 기타 → 항상 list[dict]로 normalize
    - old/new 조문목록, NLIC 응답의 단일 객체 등 처리에 사용
    """
    if not v:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, dict):
        return [v]
    return []
