from schemas import TrendVideoSourceRequest


OUTPUT_JSON_SCHEMA = """
{
  "sourceChannel": "...",
  "sourceTitle": "...",
  "sourceUrl": "...",
  "country": "KR",
  "targetGeneration": "...",
  "trendNames": ["..."],
  "memeKeywords": ["..."],
  "contentFormat": "예: 밈 설명형 숏폼 / 트렌드 큐레이션형 / 상황 공감형",
  "hookStyle": "예: 첫 3초 공감 질문형 훅",
  "phraseStyle": "예: 짧고 직관적인 자막형 문장",
  "narrativeStructure": "예: 유행어 제시 → 뜻 설명 → 사용 예시 → 공감 포인트 → 활용 맥락",
  "editingStyle": "예: 0-2초 훅 자막 → 2-7초 빠른 상황 컷 → 7-12초 반전/공감 → 12-15초 댓글 유도",
  "musicMood": "예: 경쾌함, 빠른 템포, 밝은 분위기",
  "musicSignals": ["제목/설명/자막에서 추출한 음악 관련 신호"],
  "safeMusicDirection": "예: 원곡 대신 저작권 클리어된 120-140 BPM 밝은 댄스 팝 루프",
  "thumbnailStyle": "예: 큰 키워드, 표정/상황 강조, 대비 강한 문구",
  "visualStyle": "예: 자막 중심, 밈 이미지 느낌, 짧은 장면 전환",
  "targetEmotions": ["공감", "호기심", "웃음"],
  "marketingUseCases": ["적금", "카드", "앱서비스", "소비관리"],
  "suitableProductTypes": ["적금", "카드", "앱서비스"],
  "copyrightRiskNotes": ["특정 문구/음악/썸네일 구도 직접 복제 금지"],
  "financialAdRiskNotes": ["청년 세대를 조롱하는 표현 주의", "수익 보장 표현 금지"],
  "exampleSafeHooks": ["월급 관리, 나만 어려운 거 아니죠?", "이번 달 소비 패턴 점검해볼까요?"],
  "freshnessScore": 0,
  "trendScore": 0
}
"""


def build_trend_video_analysis_prompt(request: TrendVideoSourceRequest) -> str:
    return f"""
Trend Video Analysis / 트렌드 영상 분석

사용자가 직접 입력한 유튜브 영상 요약문, 자막, 메모만 분석한다.
실제 유튜브 영상을 다운로드하거나 크롤링하지 않는다.

반드시 지킬 것:
- 원문 문구 복사 금지
- 음악 제목/음원 자체 복제 금지
- 음악은 제목/설명/자막에 나타난 신호만 근거로 분위기와 템포를 추정할 것
- 특정 곡명, 멜로디, 원본 음원을 추천하지 말고 저작권 안전한 대체 음악 방향을 제시할 것
- 영상 편집 스타일은 추상화해서 설명
- 썸네일 스타일도 복제하지 않고 구조만 추출
- 원본을 복제하지 않되, 훅 타이밍, 장면 전환 리듬, 자막 밀도, 감정 전환, 댓글/참여 유도 방식은 최대한 구체적으로 추출
- 광고 기획자가 같은 트렌드 문법을 새 소재로 재구성할 수 있게 구조 중심으로 분석
- 금융광고에 쓸 때 주의할 점 포함
- freshnessScore, trendScore는 백엔드가 업로드일/조회수/좋아요/댓글/쇼츠 신호로 다시 계산하므로 임의 추정하지 말 것
- 결과는 반드시 JSON만 출력

입력:
- videoUrl: {request.videoUrl}
- videoTitle: {request.videoTitle}
- channelName: {request.channelName}
- publishedAt: {request.publishedAt}
- summaryText: {request.summaryText}
- transcriptText: {request.transcriptText}
- musicMemo: {request.musicMemo}
- editingMemo: {request.editingMemo}
- thumbnailMemo: {request.thumbnailMemo}
- targetGeneration: {request.targetGeneration}
- category: {request.category}

출력 JSON 형식:
{OUTPUT_JSON_SCHEMA}
"""


def build_trend_video_batch_analysis_prompt(requests: list[TrendVideoSourceRequest]) -> str:
    inputs = []
    for index, request in enumerate(requests, start=1):
        inputs.append(
            f"""
[SOURCE {index}]
- videoUrl: {request.videoUrl}
- videoTitle: {request.videoTitle}
- channelName: {request.channelName}
- publishedAt: {request.publishedAt}
- summaryText: {request.summaryText}
- transcriptText: {request.transcriptText}
- musicMemo: {request.musicMemo}
- editingMemo: {request.editingMemo}
- thumbnailMemo: {request.thumbnailMemo}
- targetGeneration: {request.targetGeneration}
- category: {request.category}
"""
        )

    return f"""
Trend Video Batch Analysis / 트렌드 영상 일괄 분석

아래 여러 개의 숏폼/릴스 소스를 한 번에 분석한다.
각 SOURCE마다 독립적인 트렌드 패턴 JSON 객체를 1개씩 생성한다.

반드시 지킬 것:
- 원문 문구 복사 금지
- 음악 제목/음원 자체 복제 금지
- 원본 링크는 출처 식별용으로만 사용하고, 문구/구도/음악을 직접 복제하지 말 것
- 훅 타이밍, 장면 전환 리듬, 자막 밀도, 감정 전환, 댓글/참여 유도 방식은 구조 중심으로 추출
- 금융광고에 쓸 때 주의할 점 포함
- freshnessScore, trendScore는 백엔드가 다시 계산하므로 0으로 둬도 됨
- 결과는 반드시 JSON만 출력

입력:
{''.join(inputs)}

출력 JSON 형식:
{{
  "patterns": [
    {OUTPUT_JSON_SCHEMA}
  ]
}}
"""
