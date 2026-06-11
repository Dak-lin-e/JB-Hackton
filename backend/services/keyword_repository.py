import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
KEYWORD_FILE = DATA_DIR / "trend_search_keywords.json"

DEFAULT_KEYWORDS = [
    "요즘 밈 쇼츠",
    "요즘 유행하는 챌린지",
    "요즘 20대 유행어",
    "요즘 Z세대 밈",
    "인스타 릴스 유행",
    "틱톡 챌린지",
    "쇼츠 밈",
    "숏폼 트렌드",
    "월급 밈 쇼츠",
    "텅장 밈",
    "소비 밈",
    "절약 챌린지",
    "사회초년생 밈",
    "직장인 공감 쇼츠",
    "POV 쇼츠 직장인",
    "사람 특 밈 월급",
    "MBTI 밈",
    "밸런스게임 쇼츠",
    "공감 릴스",
    "브랜드 쇼츠 광고",
]


def _normalize_keywords(keywords: list[str]) -> list[str]:
    seen = set()
    normalized = []
    for keyword in keywords:
        value = str(keyword).strip()
        if value and value not in seen:
            normalized.append(value)
            seen.add(value)
    return normalized


def ensure_keyword_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not KEYWORD_FILE.exists():
        reset_default_keywords()


def load_default_keywords() -> list[str]:
    ensure_keyword_file()
    try:
        data = json.loads(KEYWORD_FILE.read_text(encoding="utf-8") or "[]")
        keywords = _normalize_keywords(data if isinstance(data, list) else [])
    except json.JSONDecodeError:
        keywords = []
    if not keywords:
        return reset_default_keywords()
    return keywords


def reset_default_keywords() -> list[str]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    keywords = _normalize_keywords(DEFAULT_KEYWORDS)
    KEYWORD_FILE.write_text(json.dumps(keywords, ensure_ascii=False, indent=2), encoding="utf-8")
    return keywords
