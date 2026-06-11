import os
import urllib.parse
from datetime import datetime, timedelta, timezone

from services.keyword_repository import load_default_keywords
from services.youtube_data_client import _get, parse_iso8601_duration_to_seconds

MOCK_TITLES = [
    "요즘 밈 쇼츠 모음｜월급 사라지는 사람 특",
    "직장인 공감 쇼츠｜텅장 되는 과정",
    "요즘 유행하는 챌린지 따라 해봄",
    "사회초년생 소비 밈 모음",
    "POV 첫 월급 받고 어른 된 줄 알았던 나",
    "절약 챌린지로 일주일 버티기",
    "소비 MBTI 테스트 쇼츠",
]


def _use_mock_youtube() -> bool:
    return os.getenv("USE_MOCK_YOUTUBE", "false").lower() == "true" or not os.getenv("YOUTUBE_API_KEY")


def _published_after(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat().replace("+00:00", "Z")


def _to_int(value: str | None) -> int | None:
    return int(value) if value is not None and str(value).isdigit() else None


def _normalize_video_detail(item: dict, search_keyword: str) -> dict:
    snippet = item.get("snippet", {})
    content_details = item.get("contentDetails", {})
    statistics = item.get("statistics", {})
    duration = content_details.get("duration")
    duration_seconds = parse_iso8601_duration_to_seconds(duration)
    thumbnails = snippet.get("thumbnails", {})
    thumbnail = thumbnails.get("high") or thumbnails.get("medium") or thumbnails.get("default") or {}
    video_id = item.get("id")
    return {
        "videoId": video_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "channelTitle": snippet.get("channelTitle", ""),
        "publishedAt": snippet.get("publishedAt"),
        "thumbnailUrl": thumbnail.get("url"),
        "videoUrl": f"https://www.youtube.com/watch?v={urllib.parse.quote(video_id or '')}",
        "duration": duration,
        "durationSeconds": duration_seconds,
        "viewCount": _to_int(statistics.get("viewCount")),
        "likeCount": _to_int(statistics.get("likeCount")),
        "commentCount": _to_int(statistics.get("commentCount")),
        "searchKeyword": search_keyword,
        "sourceType": "keyword",
        "sourceLabel": search_keyword,
    }


def _mock_videos_for_keyword(keyword: str, max_results: int) -> list[dict]:
    videos = []
    for index, title in enumerate(MOCK_TITLES[:max_results]):
        video_id = f"mock-{abs(hash(keyword + title)) % 1000000}-{index}"
        videos.append(
            {
                "videoId": video_id,
                "title": title,
                "description": f"{keyword} 기반 최신 숏폼 트렌드 후보 mock 데이터입니다. 쇼츠 밈 공감 챌린지 흐름을 포함합니다.",
                "channelTitle": "트렌드 샘플 채널",
                "publishedAt": datetime.now(timezone.utc).isoformat(),
                "thumbnailUrl": "https://placehold.co/480x270?text=Trend+Shorts",
                "videoUrl": f"https://www.youtube.com/watch?v={video_id}",
                "duration": "PT45S",
                "durationSeconds": 45 + (index % 10),
                "viewCount": 12000 + index * 3500,
                "likeCount": 400 + index * 80,
                "commentCount": 30 + index * 7,
                "searchKeyword": keyword,
                "sourceType": "keyword",
                "sourceLabel": keyword,
            }
        )
    return videos


def _popularity_score(video: dict) -> int:
    return (
        int(video.get("viewCount") or 0)
        + int(video.get("likeCount") or 0) * 20
        + int(video.get("commentCount") or 0) * 50
    )


def search_youtube_videos_by_keyword(keyword: str, published_within_days: int = 30, max_results: int = 10) -> list[dict]:
    if _use_mock_youtube():
        return _mock_videos_for_keyword(keyword, max_results)

    data = _get(
        "search",
        {
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "order": os.getenv("YOUTUBE_SEARCH_ORDER", "viewCount"),
            "regionCode": os.getenv("YOUTUBE_REGION_CODE", "KR"),
            "relevanceLanguage": os.getenv("YOUTUBE_RELEVANCE_LANGUAGE", "ko"),
            "publishedAfter": _published_after(published_within_days),
            "maxResults": max_results,
        },
    )
    video_ids = [
        item.get("id", {}).get("videoId")
        for item in data.get("items", [])
        if item.get("id", {}).get("videoId")
    ]
    return get_video_details(video_ids, search_keyword=keyword)


def get_video_details(video_ids: list[str], search_keyword: str = "") -> list[dict]:
    if not video_ids:
        return []
    if _use_mock_youtube():
        return _mock_videos_for_keyword(search_keyword or "요즘 밈 쇼츠", len(video_ids))

    details = _get(
        "videos",
        {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids),
            "maxResults": min(len(video_ids), 50),
        },
    )
    return [_normalize_video_detail(item, search_keyword) for item in details.get("items", [])]


def collect_videos_by_keywords(
    keywords: list[str],
    published_within_days: int = 30,
    max_results_per_keyword: int = 10,
) -> list[dict]:
    collected = []
    seen_ids = set()
    for keyword in keywords:
        for video in search_youtube_videos_by_keyword(keyword, published_within_days, max_results_per_keyword):
            video_id = video.get("videoId")
            if video_id and video_id not in seen_ids:
                collected.append(video)
                seen_ids.add(video_id)
    return sorted(collected, key=_popularity_score, reverse=True)


def collect_videos_by_default_keywords(
    published_within_days: int = 30,
    max_results_per_keyword: int = 10,
) -> list[dict]:
    return collect_videos_by_keywords(load_default_keywords(), published_within_days, max_results_per_keyword)
