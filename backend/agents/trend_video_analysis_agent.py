import json
import os
import re
from datetime import datetime, timezone

from prompts.trend_video_analysis_prompt import build_trend_video_analysis_prompt, build_trend_video_batch_analysis_prompt
from schemas import TrendVideoSourceRequest
from services.llm_client import call_llm
from services.trend_video_repository import add_trend_video_pattern
from services.trend_vector_store import upsert_trend_pattern_embedding

REQUIRED_LIST_FIELDS = [
    "trendNames",
    "memeKeywords",
    "targetEmotions",
    "marketingUseCases",
    "suitableProductTypes",
    "copyrightRiskNotes",
    "financialAdRiskNotes",
    "exampleSafeHooks",
    "musicSignals",
]


def _clamp_score(score: int) -> int:
    return max(0, min(100, score))


def _parse_metric(summary_text: str, label: str) -> int:
    match = re.search(rf"{re.escape(label)}\s*:\s*([\d,]+)", summary_text or "")
    if not match:
        return 0
    return int(match.group(1).replace(",", ""))


def _score_by_thresholds(value: int, thresholds: list[tuple[int, int]]) -> int:
    for threshold, score in thresholds:
        if value >= threshold:
            return score
    return 0


def calculate_freshness_score(request: TrendVideoSourceRequest) -> int:
    if not request.publishedAt:
        return 50

    try:
        published_at = datetime.fromisoformat(request.publishedAt.replace("Z", "+00:00"))
    except ValueError:
        return 50

    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)

    age_days = max(0, (datetime.now(timezone.utc) - published_at).days)
    if age_days <= 3:
        return 100
    if age_days <= 7:
        return 90
    if age_days <= 14:
        return 75
    if age_days <= 30:
        return 60
    if age_days <= 60:
        return 40
    return 20


def calculate_trend_score(request: TrendVideoSourceRequest) -> int:
    summary_text = request.summaryText or ""
    views = _parse_metric(summary_text, "조회수")
    likes = _parse_metric(summary_text, "좋아요 수")
    comments = _parse_metric(summary_text, "댓글 수")

    score = _score_by_thresholds(
        views,
        [
            (5_000_000, 45),
            (1_000_000, 38),
            (500_000, 32),
            (100_000, 25),
            (10_000, 15),
            (1_000, 8),
            (1, 3),
        ],
    )
    score += _score_by_thresholds(
        likes,
        [
            (100_000, 20),
            (50_000, 17),
            (10_000, 14),
            (1_000, 10),
            (100, 5),
            (1, 1),
        ],
    )
    score += _score_by_thresholds(
        comments,
        [
            (5_000, 15),
            (1_000, 12),
            (100, 8),
            (10, 4),
            (1, 1),
        ],
    )

    lower_summary = summary_text.lower()
    if (
        "60초 이하" in summary_text
        or "shorts" in lower_summary
        or "쇼츠" in summary_text
        or "reels" in lower_summary
        or "릴스" in summary_text
        or "clips" in lower_summary
    ):
        score += 8
    if any(keyword in lower_summary for keyword in ["챌린지", "밈", "유행", "pov", "릴스", "tiktok"]):
        score += 5
    if request.musicMemo and "음악 메타데이터 없음" not in request.musicMemo:
        score += 4
    if request.transcriptText or "자막: 추출 실패" not in summary_text:
        score += 3

    return _clamp_score(score)


def _fallback_pattern(request: TrendVideoSourceRequest) -> dict:
    return {
        "sourceChannel": request.channelName,
        "sourceTitle": request.videoTitle,
        "sourceUrl": request.videoUrl,
        "country": "KR",
        "targetGeneration": request.targetGeneration,
        "trendNames": [request.videoTitle],
        "memeKeywords": ["공감", "밈", "트렌드 설명"],
        "contentFormat": "트렌드 큐레이션형",
        "hookStyle": "공감형 질문 훅",
        "phraseStyle": "짧은 자막형 문장",
        "narrativeStructure": "트렌드 제시 → 의미 설명 → 사용 맥락 → 광고 활용",
        "editingStyle": request.editingMemo or "빠른 컷 편집과 자막 중심",
        "musicMood": request.musicMemo or "밝고 경쾌한 분위기",
        "musicSignals": [request.musicMemo] if request.musicMemo else ["특정 음원 신호 없음"],
        "safeMusicDirection": request.musicMemo or "저작권 클리어된 밝은 숏폼 BGM",
        "thumbnailStyle": request.thumbnailMemo or "큰 키워드 중심",
        "visualStyle": "자막 중심의 숏폼 스타일",
        "targetEmotions": ["공감", "호기심", "웃음"],
        "marketingUseCases": ["적금", "카드", "앱서비스"],
        "suitableProductTypes": ["적금", "카드", "앱서비스"],
        "copyrightRiskNotes": ["원본 문구/음악/썸네일 직접 복제 금지"],
        "financialAdRiskNotes": ["수익 보장 표현 금지", "세대 조롱 표현 주의"],
        "exampleSafeHooks": ["이번 달 소비 패턴 점검해볼까요?"],
        "freshnessScore": 75,
        "trendScore": 75,
    }


def _normalize_pattern(pattern: dict, request: TrendVideoSourceRequest) -> dict:
    normalized = {**_fallback_pattern(request), **pattern}
    normalized["sourceChannel"] = normalized.get("sourceChannel") or request.channelName
    normalized["sourceTitle"] = normalized.get("sourceTitle") or request.videoTitle
    normalized["sourceUrl"] = normalized.get("sourceUrl") or request.videoUrl
    normalized["sourcePublishedAt"] = request.publishedAt
    normalized["country"] = normalized.get("country") or "KR"
    normalized["targetGeneration"] = normalized.get("targetGeneration") or request.targetGeneration
    for field in REQUIRED_LIST_FIELDS:
        if not isinstance(normalized.get(field), list):
            normalized[field] = [str(normalized.get(field))]
    normalized["freshnessScore"] = calculate_freshness_score(request)
    normalized["trendScore"] = calculate_trend_score(request)
    normalized["safeMusicDirection"] = normalized.get("safeMusicDirection") or normalized.get("musicMood")
    now = datetime.now(timezone.utc).isoformat()
    normalized["createdAt"] = normalized.get("createdAt") or now
    normalized["updatedAt"] = normalized.get("updatedAt") or now
    return normalized


def analyze_trend_video_source(request: TrendVideoSourceRequest) -> dict:
    prompt = build_trend_video_analysis_prompt(request)
    try:
        parsed = json.loads(call_llm(prompt, model=os.getenv("OPENAI_MODEL_TREND")))
    except json.JSONDecodeError:
        parsed = _fallback_pattern(request)
    pattern = _normalize_pattern(parsed, request)
    saved_pattern = add_trend_video_pattern(pattern)
    upsert_trend_pattern_embedding(saved_pattern)
    return saved_pattern


def _extract_batch_patterns(parsed) -> list[dict]:
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict) and isinstance(parsed.get("patterns"), list):
        return parsed["patterns"]
    return []


def analyze_trend_video_sources(requests: list[TrendVideoSourceRequest]) -> list[dict]:
    if not requests:
        return []
    if len(requests) == 1:
        return [analyze_trend_video_source(requests[0])]

    prompt = build_trend_video_batch_analysis_prompt(requests)
    try:
        parsed = json.loads(call_llm(prompt, model=os.getenv("OPENAI_MODEL_TREND")))
        raw_patterns = _extract_batch_patterns(parsed)
    except json.JSONDecodeError:
        raw_patterns = []

    saved_patterns = []
    for index, request in enumerate(requests):
        raw_pattern = raw_patterns[index] if index < len(raw_patterns) and isinstance(raw_patterns[index], dict) else {}
        pattern = _normalize_pattern(raw_pattern or _fallback_pattern(request), request)
        saved_pattern = add_trend_video_pattern(pattern)
        upsert_trend_pattern_embedding(saved_pattern)
        saved_patterns.append(saved_pattern)
    return saved_patterns
