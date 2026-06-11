import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent.parent / ".runtime"
DATA_DIR = Path(os.getenv("TREND_DATA_DIR", DEFAULT_DATA_DIR))
DATA_FILE = DATA_DIR / "trend_video_patterns.json"
DEFAULT_RETENTION_DAYS = 30
DEFAULT_MIN_FRESHNESS_SCORE = 40


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _retention_days() -> int:
    try:
        return max(1, int(os.getenv("TREND_PATTERN_RETENTION_DAYS", DEFAULT_RETENTION_DAYS)))
    except ValueError:
        return DEFAULT_RETENTION_DAYS


def _min_freshness_score() -> int:
    try:
        return max(0, min(100, int(os.getenv("TREND_PATTERN_MIN_FRESHNESS_SCORE", DEFAULT_MIN_FRESHNESS_SCORE))))
    except ValueError:
        return DEFAULT_MIN_FRESHNESS_SCORE


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_trend_video_patterns() -> list[dict]:
    ensure_data_file()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8") or "[]")
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_trend_video_patterns(patterns: list[dict]) -> None:
    ensure_data_file()
    DATA_FILE.write_text(json.dumps(patterns, ensure_ascii=False, indent=2), encoding="utf-8")


def _pattern_key(pattern: dict) -> str:
    return pattern.get("sourceUrl") or pattern.get("sourceTitle") or pattern.get("id", "")


def _dedupe_patterns(patterns: list[dict]) -> list[dict]:
    deduped_by_key = {}
    for pattern in sorted(patterns, key=lambda item: item.get("updatedAt", "")):
        key = _pattern_key(pattern)
        if key:
            deduped_by_key[key] = pattern
    return sorted(deduped_by_key.values(), key=lambda item: item.get("updatedAt", ""), reverse=True)


def prune_stale_trend_video_patterns(patterns: list[dict]) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=_retention_days())
    min_freshness_score = _min_freshness_score()
    fresh_patterns = []

    for pattern in patterns:
        freshness_score = int(pattern.get("freshnessScore") or 0)
        if freshness_score < min_freshness_score:
            continue

        reference_date = (
            _parse_iso_datetime(pattern.get("sourcePublishedAt"))
            or _parse_iso_datetime(pattern.get("updatedAt"))
            or _parse_iso_datetime(pattern.get("createdAt"))
        )
        if reference_date and reference_date < cutoff:
            continue

        fresh_patterns.append(pattern)

    return _dedupe_patterns(fresh_patterns)


def add_trend_video_pattern(pattern: dict) -> dict:
    patterns = prune_stale_trend_video_patterns(load_trend_video_patterns())
    now = _now_iso()
    saved_pattern = {
        **pattern,
        "id": pattern.get("id") or str(uuid4()),
        "createdAt": pattern.get("createdAt") or now,
        "updatedAt": pattern.get("updatedAt") or now,
    }
    saved_key = _pattern_key(saved_pattern)
    patterns = [
        item
        for item in patterns
        if item.get("id") != saved_pattern["id"] and _pattern_key(item) != saved_key
    ]
    patterns.append(saved_pattern)
    save_trend_video_patterns(prune_stale_trend_video_patterns(patterns))
    return saved_pattern


def get_recent_trend_video_patterns(limit: int = 10) -> list[dict]:
    return prune_stale_trend_video_patterns(load_trend_video_patterns())[:limit]


def get_trend_video_pattern_by_id(pattern_id: str) -> dict | None:
    return next((item for item in load_trend_video_patterns() if item.get("id") == pattern_id), None)
