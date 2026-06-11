import os

from agents.trend_video_analysis_agent import analyze_trend_video_sources
from schemas import CollectYouTubeTrendsRequest, TrendVideoSourceRequest
from services.instagram_trending_langchain_client import collect_instagram_trending_posts

DEFAULT_INSTAGRAM_RECOMMENDATION_LIMIT = 3


def _int_value(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _post_url(post: dict) -> str:
    if post.get("url"):
        return post["url"]
    code = post.get("code")
    return f"https://www.instagram.com/reel/{code}/" if code else ""


def _to_frontend_video(post: dict) -> dict:
    is_reel = bool(post.get("is_video")) or post.get("type") == "clips"
    source_url = _post_url(post)
    return {
        "videoId": str(post.get("id") or post.get("code") or source_url),
        "videoUrl": source_url,
        "sourceUrl": source_url,
        "sourceCode": post.get("code"),
        "mediaUrl": post.get("video_url") or post.get("image_url"),
        "title": post.get("caption") or f"{post.get('section') or 'Instagram'} · {post.get('topic') or 'Trending'}",
        "channelTitle": f"@{post.get('username')}" if post.get("username") else "Instagram Explore",
        "publishedAt": post.get("date") or post.get("processed_at"),
        "description": post.get("caption") or "",
        "duration": str(post.get("duration") or ""),
        "durationSeconds": _int_value(post.get("duration")),
        "viewCount": _int_value(post.get("plays")),
        "likeCount": _int_value(post.get("likes")),
        "commentCount": _int_value(post.get("comments")),
        "thumbnailUrl": post.get("thumbnail_url") or post.get("image_url"),
        "transcriptText": post.get("caption") or "",
        "transcriptStatus": "caption",
        "searchKeyword": post.get("topic") or post.get("section") or "Instagram Explore",
        "sourceType": "instagram",
        "sourceLabel": "Instagram Explore",
        "isShortsCandidate": is_reel,
        "shortsReason": "Instagram Reels/Explore 영상 후보" if is_reel else "Instagram Explore 피드/캐러셀 후보",
    }


def analyze_instagram_trends_from_apify(request: CollectYouTubeTrendsRequest) -> dict:
    max_results = max(10, (request.maxResultsPerKeyword or 2) * 5)
    analysis_limit = request.analysisLimit or DEFAULT_INSTAGRAM_RECOMMENDATION_LIMIT
    posts = collect_instagram_trending_posts(
        max_results=max_results,
        country=os.getenv("APIFY_INSTAGRAM_COUNTRY", "South Korea"),
        download_medias=os.getenv("APIFY_INSTAGRAM_DOWNLOAD_MEDIAS", "none"),
    )
    ranked_posts = sorted(
        posts,
        key=lambda post: _int_value(post.get("plays")) + _int_value(post.get("likes")) * 20 + _int_value(post.get("comments")) * 50,
        reverse=True,
    )
    analysis_candidates = ranked_posts[:analysis_limit]
    videos = [_to_frontend_video(post) for post in ranked_posts]
    trend_requests = []
    for post in analysis_candidates:
        video = _to_frontend_video(post)
        summary_parts = [
            f"플랫폼: Instagram Explore",
            f"원본 릴스/게시물 URL: {video['sourceUrl']}",
            f"Instagram shortcode: {post.get('code') or ''}",
            f"Explore 섹션: {post.get('section') or ''}",
            f"Explore 토픽: {post.get('topic') or ''}",
            f"작성자: {post.get('username') or ''}",
            f"콘텐츠 타입: {post.get('type') or ''}",
            f"캡션: {post.get('caption') or ''}",
            f"조회수: {_int_value(post.get('plays'))}",
            f"좋아요 수: {_int_value(post.get('likes'))}",
            f"댓글 수: {_int_value(post.get('comments'))}",
            f"Reels 판별 이유: {video['shortsReason']}",
            f"음악 관련 신호: has_audio={post.get('has_audio')}, duration={post.get('duration')}",
            f"미디어 URL 참고값: {video.get('mediaUrl') or ''}",
        ]
        trend_requests.append(
            TrendVideoSourceRequest(
                videoUrl=video["videoUrl"],
                videoTitle=video["title"],
                channelName=video["channelTitle"],
                publishedAt=video.get("publishedAt"),
                transcriptText=post.get("caption") or "",
                summaryText="\n".join(summary_parts),
                musicMemo=(
                    "Instagram Explore 메타데이터 기준 오디오 포함"
                    if post.get("has_audio")
                    else "음악 메타데이터 없음"
                ),
                editingMemo="Instagram Reels/Explore 형식의 훅, 캡션, 주제, 참여 신호를 구조화",
                thumbnailMemo="이미지/썸네일 URL은 복제하지 않고 색감과 구도 문법만 추상화",
                targetGeneration="MZ세대",
                category="Instagram 최신 트렌드",
            )
        )

    analyzed_patterns = analyze_trend_video_sources(trend_requests)

    return {
        "sourceMode": "instagramApifyLangChain",
        "keywordsUsed": ["Instagram Explore", "Reels", "Trending"],
        "totalCollected": len(posts),
        "totalShortsCandidates": sum(1 for video in videos if video.get("isShortsCandidate")),
        "fetchedVideoCount": len(posts),
        "shortsCount": sum(1 for video in videos if video.get("isShortsCandidate")),
        "recommendationLimit": analysis_limit,
        "analyzedVideoCount": len(analyzed_patterns),
        "videos": videos[: max(analysis_limit, 3)],
        "patterns": analyzed_patterns,
    }
