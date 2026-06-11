import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

SERVICE_DIR = Path(__file__).resolve().parent
load_dotenv(SERVICE_DIR.parent / ".env")
load_dotenv(SERVICE_DIR.parent.parent / ".env")


def _trend_video_pattern_mock() -> dict:
    return {
        "sourceChannel": "YouTube 트렌드",
        "sourceTitle": "샘플 트렌드/밈 설명 영상",
        "sourceUrl": None,
        "country": "KR",
        "targetGeneration": "MZ세대",
        "trendNames": ["밈 설명형 콘텐츠", "공감형 숏폼"],
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
        "marketingUseCases": ["적금", "카드", "앱서비스", "소비관리"],
        "suitableProductTypes": ["적금", "카드", "앱서비스"],
        "copyrightRiskNotes": ["원본 문구, 음악, 썸네일 직접 복제 금지"],
        "financialAdRiskNotes": ["수익 보장 표현 금지", "세대 조롱 표현 주의"],
        "exampleSafeHooks": ["이번 달 소비, 나만 이런 거 아니죠?", "소비 루틴 한번 점검해볼까요?"],
        "freshnessScore": 80,
        "trendScore": 80,
    }


def _creative_plan_mock() -> dict:
    return {
        "campaignConcept": "공감형 숏폼 문법을 활용해 금융 루틴의 필요성을 안전하게 제안하는 캠페인",
        "usedTrendPatterns": ["밈 설명형 콘텐츠"],
        "coreMessage": "소비 공감에서 시작해 조건 확인과 금융 루틴 형성으로 연결",
        "videoCreative": {
            "format": "YouTube Shorts / Instagram Reels / TikTok",
            "duration": "15초",
            "sceneByScene": [
                {
                    "time": "0-3초",
                    "visualDirection": "통장 잔액을 확인하는 짧은 상황 컷",
                    "caption": "이번 달 소비, 나만 어려운 거 아니죠?",
                    "narration": "월급 관리를 처음 시작한다면",
                    "musicMood": "밝고 경쾌한 분위기",
                    "editingDirection": "빠른 컷 전환과 큰 자막 강조",
                },
                {
                    "time": "4-10초",
                    "visualDirection": "소비 항목이 자막 카드로 쌓이는 장면",
                    "caption": "작은 소비도 모이면 꽤 커집니다",
                    "narration": "먼저 관리하는 루틴이 필요합니다",
                    "musicMood": "가벼운 템포",
                    "editingDirection": "자막 중심 리듬 편집",
                },
                {
                    "time": "11-15초",
                    "visualDirection": "상품 혜택과 조건을 간결하게 제시",
                    "caption": "조건 확인 후 내 금융 루틴 시작",
                    "narration": "혜택과 유의사항을 확인해보세요",
                    "musicMood": "밝고 안정적인 마무리",
                    "editingDirection": "CTA와 유의사항 동시 노출",
                },
            ],
            "shootingGuide": "실제 상품 화면 대신 추상적인 금융 루틴 상황을 촬영",
            "editingGuide": "원본 영상 구도 복제 없이 짧은 컷, 큰 자막, 리듬감만 참고",
            "musicGuide": "특정 곡이 아닌 밝고 경쾌한 템포만 제안",
            "thumbnailCopy": "이번 달 소비 루틴 점검",
            "thumbnailDirection": "큰 키워드와 간단한 상황 아이콘 중심",
        },
        "imageCreative": {
            "instagramFeedCopy": "소비 루틴, 이번 달부터 가볍게 점검해볼까요?",
            "cardNewsCopies": [
                "1장: 이번 달 소비, 나만 어려운 거 아니죠?",
                "2장: 작은 소비가 쌓이면 관리가 필요합니다.",
                "3장: 상품 혜택과 조건을 함께 확인하세요.",
                "4장: 유의사항까지 보고 선택하세요.",
                "5장: 내 금융 루틴 시작하기",
            ],
            "visualDirection": "밝은 배경, 큰 자막, 금융 루틴 아이콘 중심",
            "layoutGuide": "5장 카드뉴스, 각 장 1메시지 원칙",
            "safeImagePrompt": "Korean fintech ad card, bright clean dashboard style, big readable Korean placeholder text, no copyrighted character, no copied thumbnail composition",
        },
        "adCopies": {
            "instagramCaption": "이번 달 소비, 나만 어려운 거 아니죠? 조건과 유의사항을 확인하고 내 금융 루틴을 시작해보세요.",
            "youtubeShortsTitle": "소비 루틴 점검이 필요한 순간",
            "tiktokCopy": "월급 관리는 어렵지만 루틴은 만들 수 있어요. 조건 확인부터.",
            "cta": "조건 확인하기",
            "hashtags": ["#금융루틴", "#MZ재테크", "#소비관리", "#금융습관"],
        },
        "abTests": [
            {
                "name": "A안",
                "type": "밈/공감형",
                "hook": "이번 달 소비, 나만 어려운 거 아니죠?",
                "message": "공감으로 유입 후 상품 조건을 안내",
                "recommendedChannel": "인스타그램 릴스",
                "strength": "초반 공감 반응 유도",
                "caution": "세대 조롱처럼 보이지 않게 표현 조절",
            },
            {
                "name": "B안",
                "type": "혜택/정보형",
                "hook": "혜택보다 먼저 조건을 확인하세요",
                "message": "혜택, 가입조건, 유의사항을 명확히 전달",
                "recommendedChannel": "유튜브 쇼츠",
                "strength": "전환 설득력",
                "caution": "최고/최대 표현 기준 명시",
            },
            {
                "name": "C안",
                "type": "참여/댓글유도형",
                "hook": "내 소비 루틴 점수는 몇 점?",
                "message": "참여형 질문으로 댓글과 저장을 유도",
                "recommendedChannel": "틱톡",
                "strength": "참여 반응 확대",
                "caution": "개인 금융정보 노출 유도 금지",
            },
        ],
        "copyrightSafetyNotes": ["원본 문구, 음악, 썸네일 구도 직접 복제 금지", "구조와 분위기만 참고"],
        "financialAdSafetyNotes": ["수익 보장 표현 금지", "가입 조건과 주의사항 병기"],
    }


def _compliance_mock() -> dict:
    return {
        "riskLevel": "medium",
        "issues": [
            {
                "text": "이번 달 소비, 나만 어려운 거 아니죠?",
                "riskType": "과도한 불안 조성 가능성",
                "severity": "medium",
                "reason": "공감형 질문이지만 반복 사용 시 불안 자극으로 읽힐 수 있습니다.",
                "revision": "이번 달 소비 루틴을 가볍게 점검해볼까요?",
            },
            {
                "text": "원본 영상 스타일 참고",
                "riskType": "저작권 모방 위험",
                "severity": "low",
                "reason": "구조와 분위기만 참고하도록 명시되어 직접 복제 위험이 낮습니다.",
                "revision": "특정 자막 문구, 음악, 썸네일 구도는 사용하지 않습니다.",
            },
        ],
        "finalRecommendation": "조건, 유의사항, 저작권 안전 메모를 광고안 하단에 함께 배치하세요.",
        "copyrightSafetyRecommendation": "원본 문장/음악/썸네일은 복제하지 말고 추상 패턴만 활용하세요.",
        "financialAdSafetyRecommendation": "혜택은 조건부로 설명하고 가입 조건과 주의사항을 병기하세요.",
    }


def _performance_mock() -> dict:
    return {
        "summary": "공감형 훅은 조회 반응에, 혜택/정보형은 전환 설득에 유리합니다.",
        "bestCtrVariant": "A안",
        "bestConversionVariant": "B안",
        "recommendation": "A안의 공감형 훅과 B안의 조건 설명 구조를 결합하세요.",
        "nextCampaignStrategy": "Before/After 구조로 사용 전후 변화를 보여주는 패턴을 추천합니다.",
    }


def _extract_response_text(response) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    output = getattr(response, "output", None) or []
    chunks = []
    for item in output:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                chunks.append(text)
    return "\n".join(chunks)


def _call_openai(prompt: str, model: str | None = None) -> str:
    selected_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.responses.create(
        model=selected_model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a Korean AI marketing agent for financial advertising. "
                    "Return only valid JSON. Do not include markdown fences or commentary. "
                    "Do not copy copyrighted video phrases, music, thumbnails, or exact editing compositions."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        text={"format": {"type": "json_object"}},
    )
    text = _extract_response_text(response).strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    json.loads(text)
    return text


def call_llm(prompt: str, model: str | None = None) -> str:
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    api_key = os.getenv("OPENAI_API_KEY")
    if use_mock or not api_key:
        if "Creative Planning" in prompt or "광고 제작 기획안" in prompt:
            return json.dumps(_creative_plan_mock(), ensure_ascii=False)
        if "금융광고 심의" in prompt or "Compliance" in prompt:
            return json.dumps(_compliance_mock(), ensure_ascii=False)
        if "Trend Video Analysis" in prompt or "트렌드 영상 분석" in prompt:
            return json.dumps(_trend_video_pattern_mock(), ensure_ascii=False)
        return json.dumps(_performance_mock(), ensure_ascii=False)

    return _call_openai(prompt, model=model)
