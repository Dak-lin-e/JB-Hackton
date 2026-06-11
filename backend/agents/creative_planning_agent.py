import json
import os

from prompts.creative_planning_prompt import build_creative_planning_prompt
from schemas import CreativePlanningRequest
from services.llm_client import call_llm
from services.trend_video_matcher import match_trend_video_patterns_for_campaign
from services.trend_vector_store import retrieve_relevant_trend_patterns


def _fallback_plan(request: CreativePlanningRequest, matched_patterns: list[dict]) -> dict:
    pattern_names = [
        pattern.get("sourceTitle") or ", ".join(pattern.get("trendNames", []))
        for pattern in matched_patterns
    ]
    return {
        "campaignConcept": f"{request.productName}을 {request.targetCustomer}에게 공감형 숏폼 문법으로 제안하는 캠페인",
        "usedTrendPatterns": pattern_names,
        "coreMessage": f"{request.keyBenefit}을 소개하되 가입 조건과 유의사항을 함께 안내",
        "videoCreative": {
            "format": "YouTube Shorts / Instagram Reels / TikTok",
            "duration": "15초",
            "sceneByScene": [
                {
                    "time": "0-3초",
                    "visualDirection": "소비 상황을 보여주는 짧은 컷",
                    "caption": "이번 달 소비 루틴, 점검해볼까요?",
                    "narration": "금융 루틴이 필요할 때",
                    "musicMood": matched_patterns[0].get("musicMood", "밝고 경쾌한 분위기"),
                    "editingDirection": matched_patterns[0].get("editingStyle", "빠른 컷과 자막 중심"),
                },
                {
                    "time": "4-10초",
                    "visualDirection": "상품 혜택을 자막 카드로 정리",
                    "caption": request.keyBenefit,
                    "narration": "조건을 확인하고 선택하세요",
                    "musicMood": "가벼운 템포",
                    "editingDirection": "큰 자막과 정보 카드",
                },
                {
                    "time": "11-15초",
                    "visualDirection": "CTA와 유의사항 동시 노출",
                    "caption": "가입 조건과 유의사항 확인",
                    "narration": request.caution,
                    "musicMood": "안정적인 마무리",
                    "editingDirection": "CTA 고정 노출",
                },
            ],
            "shootingGuide": "원본 영상 구도 복제 없이 금융 루틴 상황 중심",
            "editingGuide": "짧은 컷, 큰 자막, 리듬감만 참고",
            "musicGuide": "특정 곡이 아닌 분위기/템포만 제안",
            "thumbnailCopy": "소비 루틴 점검",
            "thumbnailDirection": "큰 키워드와 깔끔한 금융 UI 느낌",
        },
        "trendAdaptationNotes": [
            "첫 3초 공감형 훅, 빠른 컷 전환, 큰 자막 중심 리듬을 참고하되 문구와 상황은 금융상품에 맞게 새로 구성",
            "참여/댓글 유도형 구조는 개인 금융정보를 묻지 않는 안전한 질문으로 변환",
        ],
        "imageCreative": {
            "instagramFeedCopy": f"{request.productName}, 조건 확인하고 시작하세요.",
            "cardNewsCopies": [
                "1장: 이번 달 소비 루틴, 점검해볼까요?",
                f"2장: 핵심 혜택: {request.keyBenefit}",
                f"3장: 가입 조건: {request.eligibility}",
                f"4장: 주의사항: {request.caution}",
                "5장: 조건 확인하고 내 금융 루틴 시작",
            ],
            "visualDirection": "밝은 배경, 큰 자막, 금융 아이콘 중심",
            "layoutGuide": "5장 카드뉴스, 각 장 1메시지",
            "safeImagePrompt": "Clean Korean fintech campaign card, bright neutral background, large readable Korean placeholder text, no copyrighted character, no copied thumbnail composition",
        },
        "adCopies": {
            "instagramCaption": f"{request.productName}으로 금융 루틴을 점검해보세요. {request.eligibility} 및 유의사항을 확인하세요.",
            "youtubeShortsTitle": f"{request.productName} 금융 루틴 점검",
            "tiktokCopy": "소비 루틴이 흔들릴 때, 조건부터 확인하고 시작.",
            "cta": "조건 확인하기",
            "hashtags": ["#금융루틴", "#MZ재테크", f"#{request.productType}"],
        },
        "abTests": [
            {
                "name": "A안",
                "type": "밈/공감형",
                "hook": "이번 달 소비 루틴, 나만 흔들리나요?",
                "message": "공감으로 유입 후 상품 소개",
                "recommendedChannel": "인스타그램 릴스",
                "strength": "초반 반응 유도",
                "caution": "불안 조성 표현 주의",
            },
            {
                "name": "B안",
                "type": "혜택/정보형",
                "hook": request.keyBenefit,
                "message": "혜택과 조건을 명확히 안내",
                "recommendedChannel": "유튜브 쇼츠",
                "strength": "전환 설득",
                "caution": "조건부 표현 필요",
            },
            {
                "name": "C안",
                "type": "참여/댓글유도형",
                "hook": "내 소비 루틴 점수는?",
                "message": "참여를 유도하고 상품으로 연결",
                "recommendedChannel": "틱톡",
                "strength": "댓글 반응",
                "caution": "개인 금융정보 노출 유도 금지",
            },
        ],
        "copyrightSafetyNotes": ["원본 문구/음악/썸네일 복제 금지", "구조와 분위기만 참고"],
        "financialAdSafetyNotes": ["수익 보장 표현 금지", "가입 조건과 주의사항 병기"],
    }


def _ensure_product_grounding(plan: dict, request: CreativePlanningRequest) -> dict:
    product_summary = f"{request.productName}: {request.keyBenefit}"
    plan["campaignConcept"] = plan.get("campaignConcept") or f"{request.productName} 광고 캠페인"
    if request.productName not in plan["campaignConcept"]:
        plan["campaignConcept"] = f"{request.productName}을 중심으로 한 {plan['campaignConcept']}"

    plan["coreMessage"] = plan.get("coreMessage") or product_summary
    if request.productName not in plan["coreMessage"] and request.keyBenefit not in plan["coreMessage"]:
        plan["coreMessage"] = f"{product_summary}. {plan['coreMessage']}"
    if plan.get("usedTrendPatterns"):
        plan["coreMessage"] = (
            f"{plan['coreMessage']} 인기 숏폼에서 반복된 {', '.join(plan['usedTrendPatterns'][:3])} 구조를 "
            "상품 혜택 설명에 맞게 재구성했습니다."
        )

    video = plan.setdefault("videoCreative", {})
    video["format"] = video.get("format") or "YouTube Shorts / Instagram Reels / TikTok"
    video["duration"] = video.get("duration") or "15초"
    video["shootingGuide"] = video.get("shootingGuide") or (
        f"{request.productName}의 실제 가입 화면을 직접 노출하기보다, {request.targetCustomer}의 일상 금융 상황과 "
        "상품 혜택을 자막 카드로 연결하는 방식으로 촬영합니다."
    )
    video["editingGuide"] = video.get("editingGuide") or (
        "첫 3초는 공감 상황을 빠르게 제시하고, 중반부는 혜택/조건을 카드형 자막으로 정리하며, "
        "마지막에는 CTA와 주의사항을 함께 노출합니다."
    )
    video["musicGuide"] = video.get("musicGuide") or "특정 유행 음원을 복제하지 않고 밝고 안정적인 숏폼 템포만 사용합니다."
    if "저작권" not in video["musicGuide"]:
        video["musicGuide"] = f"{video['musicGuide']} 원본 음원은 직접 사용하지 말고 저작권 클리어 음원으로 대체합니다."
    video["thumbnailCopy"] = video.get("thumbnailCopy") or f"{request.productName} 조건 확인"
    video["thumbnailDirection"] = video.get("thumbnailDirection") or (
        "상품명, 핵심 혜택 키워드, 확인 CTA를 큰 글자로 배치하고 원본 영상 썸네일 구도는 복제하지 않습니다."
    )
    scenes = video.setdefault("sceneByScene", [])
    if not isinstance(scenes, list) or not scenes:
        scenes = [
            {
                "time": "0-3초",
                "visualDirection": f"{request.targetCustomer}가 지출 또는 금융 루틴을 확인하는 상황 컷",
                "caption": f"{request.productName}, 지금 내 금융 루틴에 맞을까요?",
                "narration": f"{request.targetCustomer}에게 필요한 금융 선택지를 점검합니다.",
                "musicMood": "밝고 빠른 숏폼 템포",
                "editingDirection": "첫 문장 자막을 크게 띄우고 빠른 컷으로 시작",
            },
            {
                "time": "4-10초",
                "visualDirection": f"{request.keyBenefit}을 카드형 자막과 아이콘으로 정리",
                "caption": f"핵심 혜택: {request.keyBenefit}",
                "narration": "혜택은 조건과 함께 확인해야 합니다.",
                "musicMood": "경쾌하지만 과장되지 않은 분위기",
                "editingDirection": "혜택, 가입 조건, 유의사항을 순서대로 정보 카드 처리",
            },
            {
                "time": "11-15초",
                "visualDirection": "CTA 버튼과 유의사항 요약을 함께 노출",
                "caption": "가입 조건과 주의사항 확인",
                "narration": f"{request.eligibility}. {request.caution}",
                "musicMood": "안정적인 마무리",
                "editingDirection": "CTA와 주의사항을 같은 화면에 고정 노출",
            },
        ]
        video["sceneByScene"] = scenes
    for index, scene in enumerate(scenes[:3]):
        caption = scene.get("caption", "")
        narration = scene.get("narration", "")
        combined = f"{caption} {narration}"
        if request.productName not in combined and request.keyBenefit not in combined:
            if index == 0:
                scene["caption"] = f"{request.productName}, 지금 내 금융 루틴에 맞을까요?"
            elif index == 1:
                scene["caption"] = f"핵심 혜택: {request.keyBenefit}"
            else:
                scene["narration"] = f"가입 조건은 {request.eligibility}. 유의사항도 함께 확인하세요."

    image = plan.setdefault("imageCreative", {})
    if not isinstance(plan.get("trendAdaptationNotes"), list) or not plan["trendAdaptationNotes"]:
        plan["trendAdaptationNotes"] = [
            "인기 숏폼의 훅 타이밍, 컷 전환 속도, 자막 밀도, 감정 전환 구조를 강하게 반영했습니다.",
            f"원본 영상의 고유 문장과 장면은 복제하지 않고 {request.productName}의 혜택/조건 중심 상황으로 재창작했습니다.",
        ]
    image["instagramFeedCopy"] = image.get("instagramFeedCopy") or f"{request.productName}, 혜택과 조건을 한 장으로 확인하세요."
    image["visualDirection"] = image.get("visualDirection") or (
        f"{request.productName}의 핵심 혜택을 금융 앱 대시보드 느낌의 깔끔한 카드 UI로 보여줍니다. "
        "실제 유튜브 썸네일이나 캐릭터는 복제하지 않고, 밝은 배경과 명확한 정보 계층을 사용합니다."
    )
    image["layoutGuide"] = image.get("layoutGuide") or (
        "상단에는 상품명, 중앙에는 핵심 혜택 1개, 하단에는 가입 조건/주의사항/CTA를 작지만 읽히는 크기로 배치합니다."
    )
    image["safeImagePrompt"] = image.get("safeImagePrompt") or (
        f"Clean Korean fintech advertisement image for {request.productName}, bright white and light gray dashboard style, "
        f"clear benefit card about {request.keyBenefit}, readable Korean placeholder text, no copyrighted character, "
        "no copied YouTube thumbnail composition, no celebrity, no brand imitation"
    )
    card_news = image.get("cardNewsCopies")
    if not isinstance(card_news, list) or len(card_news) < 5:
        image["cardNewsCopies"] = [
            f"1장: {request.productName}, 요즘 금융 루틴에 맞을까요?",
            f"2장: 핵심 혜택 - {request.keyBenefit}",
            f"3장: 가입 조건 - {request.eligibility}",
            f"4장: 주의사항 - {request.caution}",
            "5장: 조건 확인하고 시작하기",
        ]
    else:
        required_cards = [
            f"1장: {request.productName}, 요즘 금융 루틴에 맞을까요?",
            f"2장: 핵심 혜택 - {request.keyBenefit}",
            f"3장: 가입 조건 - {request.eligibility}",
            f"4장: 주의사항 - {request.caution}",
            "5장: 조건 확인하고 시작하기",
        ]
        for index, required_copy in enumerate(required_cards):
            current = str(card_news[index]) if index < len(card_news) else ""
            if index == 0 and request.productName not in current:
                card_news[index] = required_copy
            if index == 1 and request.keyBenefit not in current:
                card_news[index] = required_copy
            if index == 2 and request.eligibility not in current:
                card_news[index] = required_copy
            if index == 3 and request.caution not in current:
                card_news[index] = required_copy

    ad_copies = plan.setdefault("adCopies", {})
    instagram = ad_copies.get("instagramCaption", "")
    if request.productName not in instagram and request.keyBenefit not in instagram:
        ad_copies["instagramCaption"] = (
            f"{request.productName}으로 금융 루틴을 점검해보세요. "
            f"{request.keyBenefit} 혜택과 가입 조건을 확인하세요."
        )
    youtube_title = ad_copies.get("youtubeShortsTitle", "")
    if request.productName not in youtube_title:
        ad_copies["youtubeShortsTitle"] = f"{request.productName} 금융 루틴 점검"
    tiktok = ad_copies.get("tiktokCopy", "")
    if request.productName not in tiktok and request.keyBenefit not in tiktok:
        ad_copies["tiktokCopy"] = f"{request.productName}, {request.keyBenefit}. 조건 확인부터 가볍게 시작."
    ad_copies["cta"] = ad_copies.get("cta") or "가입 조건 확인하기"
    return plan


def _build_rag_insights(matched_patterns: list[dict]) -> list[dict]:
    insights = []
    for pattern in matched_patterns:
        rag = pattern.get("rag") or {}
        if not rag:
            continue
        insights.append(
            {
                "patternId": pattern.get("id"),
                "sourceTitle": pattern.get("sourceTitle") or ", ".join(pattern.get("trendNames", [])),
                "trendNames": pattern.get("trendNames", []),
                "reason": rag.get("reason"),
                "semanticSimilarity": rag.get("semanticSimilarity"),
                "trendScore": pattern.get("trendScore"),
                "freshnessScore": pattern.get("freshnessScore"),
                "finalScore": rag.get("finalScore"),
            }
        )
    return insights


def generate_creative_plan(request: CreativePlanningRequest) -> dict:
    matched_patterns = retrieve_relevant_trend_patterns(request)
    if not matched_patterns:
        matched_patterns = match_trend_video_patterns_for_campaign(
            request.productType,
            request.targetCustomer,
            request.campaignGoal,
            request.selectedTrendPatternId,
        )
    prompt = build_creative_planning_prompt(request, matched_patterns)
    try:
        plan = json.loads(call_llm(prompt, model=os.getenv("OPENAI_MODEL_CREATIVE")))
    except json.JSONDecodeError:
        plan = _fallback_plan(request, matched_patterns)
    if not plan.get("usedTrendPatterns"):
        plan["usedTrendPatterns"] = [
            pattern.get("sourceTitle") or ", ".join(pattern.get("trendNames", []))
            for pattern in matched_patterns
        ]
    grounded_plan = _ensure_product_grounding(plan, request)
    rag_insights = _build_rag_insights(matched_patterns)
    if rag_insights:
        grounded_plan["ragInsights"] = rag_insights
    return grounded_plan
