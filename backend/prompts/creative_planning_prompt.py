from schemas import CreativePlanningRequest


def build_creative_planning_prompt(request: CreativePlanningRequest, matched_patterns: list[dict]) -> str:
    return f"""
Creative Planning / 광고 제작 기획안

금융상품 정보와 트렌드 영상 분석 패턴을 결합해 광고 제작 기획안을 만든다.
목표는 광고 문구 몇 줄이 아니라 실제 제작자가 바로 이해할 수 있는 영상/이미지 제작 기획안이다.

반드시 지킬 것:
- 원본 영상, 문구, 음악, 썸네일을 그대로 복제하지 말 것
- 영상 스타일은 구조와 분위기만 참고할 것
- 트렌드 반영 강도는 높게 가져갈 것. 훅 타이밍, 장면 전환 속도, 자막 밀도, 감정 전환, 댓글 유도 장치는 참고 패턴과 유사한 리듬으로 설계할 것
- 단, 등장인물/상황/문장/썸네일 구도/음악/고유 개그 포인트는 금융상품과 타깃에 맞게 완전히 새로 만들 것
- 금융상품의 혜택, 가입조건, 주의사항을 왜곡하지 말 것
- 광고의 주인공은 반드시 입력된 금융상품일 것
- 참고 패턴이 여러 개라면 공통적으로 반복되는 훅, 편집 리듬, 감정, 참여 방식만 추출해 광고안에 반영할 것
- 단일 영상의 문구/상황을 베끼지 말고 여러 인기 영상에서 발견된 공통 구조를 종합할 것
- 결과에는 어떤 트렌드 구조를 어떻게 광고영상/이미지 기획에 반영했는지 명확히 설명할 것
- videoCreative.sceneByScene은 실제 숏폼 제작자가 바로 촬영할 수 있도록 초 단위 컷 구성과 자막 리듬을 구체적으로 작성할 것
- campaignConcept, coreMessage, adCopies.instagramCaption, adCopies.youtubeShortsTitle, adCopies.tiktokCopy에는 반드시 상품명 또는 핵심 혜택을 직접 언급할 것
- videoCreative.sceneByScene 중 최소 2개 장면 caption 또는 narration에 상품명/핵심 혜택/가입 조건 중 하나를 포함할 것
- imageCreative.cardNewsCopies 5장에는 상품명, 핵심 혜택, 가입 조건, 주의사항, CTA가 각각 자연스럽게 들어갈 것
- videoCreative에는 장면별 화면 연출, 촬영 소품/상황, 자막, 내레이션, 편집 방식이 구체적으로 들어갈 것
- imageCreative에는 카드뉴스/피드 이미지 제작을 위한 비주얼 방향, 레이아웃, 색감, 오브젝트, 텍스트 배치, 이미지 생성용 안전 프롬프트가 들어갈 것
- musicGuide에는 참고 패턴의 musicMood, musicSignals, safeMusicDirection을 종합해 저작권 안전한 음악 무드/BPM/효과음 방향을 제안할 것
- 특정 원곡명이나 원본 영상 음원을 그대로 쓰라고 추천하지 말 것
- 금융광고 리스크를 최소화할 것
- 결과는 JSON만 출력할 것

금융상품:
{request.model_dump_json(ensure_ascii=False)}

참고 패턴:
{matched_patterns}

참고 패턴에 rag 필드가 있다면:
- semanticSimilarity는 금융상품 입력과 트렌드 패턴의 의미 유사도다.
- finalScore가 높은 패턴을 우선 반영하되, 원본 콘텐츠의 고유 문장/장면은 복제하지 않는다.
- trendAdaptationNotes에는 왜 해당 패턴을 선택했는지와 상품 메시지로 어떻게 변환했는지 포함한다.

출력 JSON:
{{
  "campaignConcept": "...",
  "usedTrendPatterns": ["..."],
  "coreMessage": "...",
  "videoCreative": {{
    "format": "YouTube Shorts / Instagram Reels / TikTok",
    "duration": "15초",
    "sceneByScene": [
      {{
        "time": "0-3초",
        "visualDirection": "...",
        "caption": "...",
        "narration": "...",
        "musicMood": "...",
        "editingDirection": "..."
      }}
    ],
    "shootingGuide": "...",
    "editingGuide": "...",
    "musicGuide": "특정 곡이 아닌 저작권 안전 음악 무드, BPM, 효과음 방향 제안",
    "thumbnailCopy": "...",
    "thumbnailDirection": "..."
  }},
  "trendAdaptationNotes": ["참고한 트렌드 구조와 광고 소재로 바꾼 방식"],
  "imageCreative": {{
    "instagramFeedCopy": "...",
    "cardNewsCopies": ["1장...", "2장...", "3장...", "4장...", "5장..."],
    "visualDirection": "...",
    "layoutGuide": "...",
    "safeImagePrompt": "이미지 생성 도구에 넣을 수 있는 저작권 안전 프롬프트"
  }},
  "adCopies": {{
    "instagramCaption": "...",
    "youtubeShortsTitle": "...",
    "tiktokCopy": "...",
    "cta": "...",
    "hashtags": ["..."]
  }},
  "abTests": [
    {{
      "name": "A안",
      "type": "밈/공감형",
      "hook": "...",
      "message": "...",
      "recommendedChannel": "...",
      "strength": "...",
      "caution": "..."
    }}
  ],
  "copyrightSafetyNotes": ["..."],
  "financialAdSafetyNotes": ["..."]
}}
"""
