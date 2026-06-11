from agents.trend_video_analysis_agent import analyze_trend_video_source
from schemas import CollectYouTubeTrendsRequest, TrendVideoSourceRequest
from agents.youtube_collector_agent import collect_youtube_trend_candidates
from services.music_signal_extractor import extract_music_signal
from services.youtube_transcript_service import fetch_transcript_text

TREND_RECOMMENDATION_LIMIT = 3


def analyze_keyword_trend_shorts_from_youtube(request: CollectYouTubeTrendsRequest) -> dict:
    collection = collect_youtube_trend_candidates(
        published_within_days=request.publishedWithinDays or 30,
        max_results_per_keyword=request.maxResultsPerKeyword or 2,
        include_non_shorts=request.includeNonShorts,
    )
    analyzed_patterns = []
    videos_with_transcript = []
    analysis_candidates = [
        video
        for video in collection["videos"]
        if video.get("isShortsCandidate") or request.includeNonShorts
    ][: request.analysisLimit or TREND_RECOMMENDATION_LIMIT]

    for video in analysis_candidates:
        transcript_text, transcript_status = fetch_transcript_text(video["videoId"])
        video_with_transcript = {
            **video,
            "transcriptText": transcript_text,
            "transcriptStatus": transcript_status,
        }
        music_signal = extract_music_signal(video, transcript_text)
        video_with_transcript["musicSignal"] = music_signal
        videos_with_transcript.append(video_with_transcript)

        summary_parts = [
            f"검색 키워드: {video.get('searchKeyword')}",
            f"제목: {video.get('title')}",
            f"설명: {video.get('description') or ''}",
            f"채널명: {video.get('channelTitle')}",
            f"조회수: {video.get('viewCount')}",
            f"좋아요 수: {video.get('likeCount')}",
            f"댓글 수: {video.get('commentCount')}",
            f"Shorts 판별 이유: {video.get('shortsReason')}",
            f"음악 관련 신호: {music_signal}",
        ]
        if transcript_text:
            summary_parts.append(f"자막: {transcript_text[:4000]}")
        else:
            summary_parts.append("자막: 추출 실패 또는 제공되지 않음")

        pattern = analyze_trend_video_source(
            TrendVideoSourceRequest(
                videoUrl=video.get("videoUrl"),
                videoTitle=video.get("title") or "YouTube 트렌드 후보 영상",
                channelName=video.get("channelTitle") or "YouTube",
                publishedAt=video.get("publishedAt"),
                transcriptText=transcript_text,
                summaryText="\n".join(summary_parts),
                musicMemo=(
                    f"{music_signal['inferredMusicMood']} / "
                    f"저작권 안전 방향: {music_signal['safeMusicDirection']} / "
                    f"근거: {', '.join(music_signal['musicEvidence']) or '음악 메타데이터 없음'}"
                ),
                editingMemo="Shorts/숏폼 형식의 전개와 자막 중심 편집 여부를 추상화",
                thumbnailMemo="썸네일 URL은 참고하지 않고 제목/메타데이터 기반으로 구조만 추정",
                targetGeneration="MZ세대",
                category="YouTube 최신 트렌드",
            )
        )
        analyzed_patterns.append(pattern)

    return {
        **collection,
        "recommendationLimit": request.analysisLimit or TREND_RECOMMENDATION_LIMIT,
        "analyzedVideoCount": len(videos_with_transcript),
        "videos": videos_with_transcript,
        "patterns": analyzed_patterns,
    }
