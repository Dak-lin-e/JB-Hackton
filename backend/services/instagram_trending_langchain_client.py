import json
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv
from langchain_apify import ApifyWrapper
from langchain_core.documents import Document

DEFAULT_INSTAGRAM_TRENDING_ACTOR_ID = "agentx/instagram-trending-scraper"
SERVICE_DIR = Path(__file__).resolve().parent
DEFAULT_CACHE_DIR = SERVICE_DIR.parent.parent / ".runtime"
DEFAULT_CACHE_FILE = DEFAULT_CACHE_DIR / "instagram_trending_cache.json"
DEFAULT_CACHE_TTL_SECONDS = 3600
load_dotenv(SERVICE_DIR.parent / ".env")
load_dotenv(SERVICE_DIR.parent.parent / ".env")


class InstagramTrendingApiError(RuntimeError):
    pass


def _ensure_apify_token() -> None:
    token = os.getenv("APIFY_API_TOKEN") or os.getenv("APIFY_API_KEY")
    if not token:
        raise InstagramTrendingApiError("APIFY_API_TOKEN 또는 APIFY_API_KEY가 설정되어 있지 않습니다.")
    os.environ["APIFY_API_TOKEN"] = token


def _document_from_item(item: dict[str, Any]) -> Document:
    caption = item.get("caption") or ""
    topic = item.get("topic") or ""
    section = item.get("section") or ""
    username = item.get("username") or ""
    content = "\n".join(
        [
            f"caption: {caption}",
            f"section: {section}",
            f"topic: {topic}",
            f"username: {username}",
            f"type: {item.get('type')}",
            f"likes: {item.get('likes')}",
            f"comments: {item.get('comments')}",
            f"plays: {item.get('plays')}",
            f"duration: {item.get('duration')}",
            f"has_audio: {item.get('has_audio')}",
        ]
    )
    return Document(page_content=content, metadata=item)


def _parse_document(document: Document) -> dict[str, Any]:
    if isinstance(document.metadata, dict) and document.metadata:
        return document.metadata
    try:
        return json.loads(document.page_content)
    except json.JSONDecodeError:
        return {"caption": document.page_content}


def _cache_file() -> Path:
    return Path(os.getenv("APIFY_INSTAGRAM_CACHE_FILE", DEFAULT_CACHE_FILE))


def _cache_ttl_seconds() -> int:
    try:
        return max(0, int(os.getenv("APIFY_INSTAGRAM_CACHE_TTL_SECONDS", DEFAULT_CACHE_TTL_SECONDS)))
    except ValueError:
        return DEFAULT_CACHE_TTL_SECONDS


def _cache_key(actor_id: str, max_results: int, country: str, download_medias: str) -> str:
    return json.dumps(
        {
            "actorId": actor_id,
            "maxResults": max_results,
            "country": country,
            "downloadMedias": download_medias,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _load_cache() -> dict[str, Any]:
    path = _cache_file()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    path = _cache_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_cached_posts(cache_key: str) -> list[dict[str, Any]] | None:
    ttl_seconds = _cache_ttl_seconds()
    if ttl_seconds <= 0:
        return None

    item = _load_cache().get(cache_key)
    if not isinstance(item, dict):
        return None

    cached_at = item.get("cachedAt")
    try:
        cached_datetime = datetime.fromisoformat(cached_at)
    except (TypeError, ValueError):
        return None

    if cached_datetime.tzinfo is None:
        cached_datetime = cached_datetime.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - cached_datetime > timedelta(seconds=ttl_seconds):
        return None

    posts = item.get("posts")
    return posts if isinstance(posts, list) else None


def _set_cached_posts(cache_key: str, posts: list[dict[str, Any]]) -> None:
    cache = _load_cache()
    cache[cache_key] = {
        "cachedAt": datetime.now(timezone.utc).isoformat(),
        "posts": posts,
    }
    _save_cache(cache)


def collect_instagram_trending_posts(
    max_results: int = 10,
    country: str = "South Korea",
    download_medias: str = "none",
) -> list[dict[str, Any]]:
    _ensure_apify_token()
    actor_id = os.getenv("APIFY_INSTAGRAM_TRENDING_ACTOR_ID", DEFAULT_INSTAGRAM_TRENDING_ACTOR_ID)
    normalized_max_results = max(10, max_results)
    cache_key = _cache_key(actor_id, normalized_max_results, country, download_medias)
    cached_posts = _get_cached_posts(cache_key)
    if cached_posts is not None:
        return cached_posts

    apify = ApifyWrapper()
    loader = apify.call_actor(
        actor_id=actor_id,
        run_input={
            "max_results": normalized_max_results,
            "download_medias": download_medias,
            "country": country,
        },
        dataset_mapping_function=_document_from_item,
    )
    try:
        posts = [_parse_document(document) for document in loader.load()]
        _set_cached_posts(cache_key, posts)
        return posts
    except Exception as exc:
        raise InstagramTrendingApiError(str(exc)) from exc
