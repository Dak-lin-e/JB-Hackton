from services.trend_video_repository import (
    get_trend_video_pattern_by_id,
    load_trend_video_patterns,
    prune_stale_trend_video_patterns,
)

DEFAULT_TREND_VIDEO_PATTERN = {
    "id": "sample-esamsip-trend-pattern",
    "sourceChannel": "YouTube 트렌드",
    "sourceTitle": "샘플 YouTube 트렌드/밈 설명 영상",
    "sourceUrl": None,
    "country": "KR",
    "targetGeneration": "MZ세대",
    "trendNames": ["밈 설명형 콘텐츠"],
    "memeKeywords": ["공감", "밈", "짧은 자막", "트렌드 설명"],
    "contentFormat": "트렌드 큐레이션형",
    "hookStyle": "첫 3초 공감 질문형 훅",
    "phraseStyle": "짧고 직관적인 자막형 문장",
    "narrativeStructure": "유행 키워드 제시 → 뜻 설명 → 사용 맥락 → 광고 메시지 연결",
    "editingStyle": "빠른 컷 전환과 자막 강조",
    "musicMood": "밝고 경쾌한 분위기",
    "thumbnailStyle": "큰 키워드와 대비 강한 문구",
    "visualStyle": "자막 중심의 숏폼 스타일",
    "targetEmotions": ["공감", "호기심", "웃음"],
    "marketingUseCases": ["적금", "카드", "앱서비스"],
    "suitableProductTypes": ["적금", "카드", "앱서비스"],
    "copyrightRiskNotes": ["원본 문구, 음악, 썸네일 직접 복제 금지"],
    "financialAdRiskNotes": ["수익 보장 표현 금지", "세대 조롱 표현 주의"],
    "exampleSafeHooks": ["이번 달 소비, 나만 이런 거 아니죠?"],
    "freshnessScore": 80,
    "trendScore": 80,
}


def _contains_any(text: str, values: list[str]) -> bool:
    return any(value and value in text for value in values)


def _score_pattern(pattern: dict, product_type: str, target_customer: str, campaign_goal: str) -> float:
    score = (pattern.get("trendScore", 0) * 0.5) + (pattern.get("freshnessScore", 0) * 0.3)
    if product_type in pattern.get("suitableProductTypes", []) or product_type in pattern.get("marketingUseCases", []):
        score += 35
    if target_customer and target_customer in pattern.get("targetGeneration", ""):
        score += 20
    if _contains_any(campaign_goal, pattern.get("marketingUseCases", [])):
        score += 10
    return score


def match_trend_video_patterns_for_campaign(
    product_type: str,
    target_customer: str,
    campaign_goal: str,
    selected_pattern_id: str | None = None,
    limit: int = 3,
) -> list[dict]:
    patterns = prune_stale_trend_video_patterns(load_trend_video_patterns())
    if selected_pattern_id:
        selected = get_trend_video_pattern_by_id(selected_pattern_id)
        fresh_pattern_ids = {item.get("id") for item in patterns}
        if selected and selected.get("id") in fresh_pattern_ids:
            others = [item for item in patterns if item.get("id") != selected_pattern_id]
            ranked = sorted(
                others,
                key=lambda item: _score_pattern(item, product_type, target_customer, campaign_goal),
                reverse=True,
            )
            return [selected, *ranked[: max(limit - 1, 0)]]

    if not patterns:
        return [DEFAULT_TREND_VIDEO_PATTERN]

    return sorted(
        patterns,
        key=lambda item: _score_pattern(item, product_type, target_customer, campaign_goal),
        reverse=True,
    )[:limit]
