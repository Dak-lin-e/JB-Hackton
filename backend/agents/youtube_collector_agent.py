import os

from services.keyword_repository import load_default_keywords
from services.youtube_service import collect_videos_by_keywords
from agents.shorts_filter_agent import filter_shorts_candidates

DEFAULT_KEYWORD_LIMIT = 3


def _keyword_limit() -> int:
    raw_value = os.getenv("MAX_TREND_KEYWORDS")
    if not raw_value:
        return DEFAULT_KEYWORD_LIMIT
    try:
        return max(1, int(raw_value))
    except ValueError:
        return DEFAULT_KEYWORD_LIMIT


def collect_youtube_trend_candidates(
    published_within_days: int = 30,
    max_results_per_keyword: int = 2,
    include_non_shorts: bool = False,
) -> dict:
    keywords = load_default_keywords()[:_keyword_limit()]
    videos = collect_videos_by_keywords(keywords, published_within_days, max_results_per_keyword)
    filtered = filter_shorts_candidates(videos, include_non_shorts)
    filtered = sorted(
        filtered,
        key=lambda video: (
            int(video.get("viewCount") or 0)
            + int(video.get("likeCount") or 0) * 20
            + int(video.get("commentCount") or 0) * 50
        ),
        reverse=True,
    )
    return {
        "sourceMode": "defaultKeywords",
        "keywordsUsed": keywords,
        "totalCollected": len(videos),
        "totalShortsCandidates": sum(1 for video in filtered if video.get("isShortsCandidate")),
        "videos": filtered,
    }
