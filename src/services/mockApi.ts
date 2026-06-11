import { trendPatterns } from '../features/new-campaign/data/trends'
import type {
  ABTestIdea,
  CampaignInput,
  ComplianceInput,
  ComplianceIssue,
  ComplianceResult,
  GeneratedAdResult,
} from '../types'

const delay = (ms = 800) => new Promise((resolve) => window.setTimeout(resolve, ms))

function buildABTests(payload: CampaignInput): ABTestIdea[] {
  return [
    {
      variant: 'A안',
      title: '밈/공감형',
      hook: '월급 들어온 지 3일 됐는데 잔액 왜 이래?',
      message: `${payload.productName}로 소비 전에 돈관리 루틴을 먼저 잡자는 메시지`,
      expectedReaction: '댓글 공감과 저장 반응이 높을 가능성',
      channel: '인스타그램 릴스, 틱톡',
      strength: '초반 이탈을 줄이고 브랜드 친밀감을 만들기 좋음',
      caution: '불안 조성이나 세대 조롱처럼 읽히지 않게 표현 조절 필요',
    },
    {
      variant: 'B안',
      title: '혜택/정보형',
      hook: `조건 맞으면 ${payload.keyBenefit}`,
      message: `${payload.productName}의 가입 조건, 혜택, 유의사항을 짧고 명확하게 정리`,
      expectedReaction: '클릭률과 가입 전환율이 안정적으로 나올 가능성',
      channel: '유튜브 쇼츠, 카드뉴스',
      strength: '금융상품 신뢰도와 전환 설득력이 높음',
      caution: '최고/최대 표현은 기준과 조건을 함께 표기해야 함',
    },
    {
      variant: 'C안',
      title: '참여/댓글유도형',
      hook: '나만 월급날 결심하고 바로 흔들리는 거 아니지?',
      message: '댓글 참여로 소비 상황을 모으고 맞춤 금융 루틴을 제안',
      expectedReaction: '댓글과 공유가 늘어 알고리즘 확산에 유리',
      channel: '틱톡, 인스타그램 릴스',
      strength: '참여 데이터를 다음 콘텐츠 인사이트로 재활용 가능',
      caution: '개인 금융상황 노출을 유도하지 않도록 질문 수위를 낮춰야 함',
    },
  ]
}

export async function mockGenerateAdCampaign(payload: CampaignInput): Promise<GeneratedAdResult> {
  await delay()

  const pattern = payload.selectedTrendPattern ?? trendPatterns[0]
  const hooks: Record<string, string> = {
    'salary-vanish': '월급 받았는데 왜 벌써 돈이 없지?',
    'spending-mbti': '내 소비 MBTI는 저축 회피형일까, 혜택 수집형일까?',
    'pov-first-job': 'POV: 첫 월급 받고 어른의 돈관리를 시작한 나',
    'three-sec-cure': '돈이 새는 느낌이 든다면 3초만 확인하세요.',
    'before-after': '금융 루틴 전과 후, 통장 표정이 달라집니다.',
    'comment-bait': '나만 월급날 결심하고 3일 뒤 흔들리는 거 아니지?',
  }
  const hook = hooks[pattern.id] ?? hooks['salary-vanish']

  return {
    concept: `${pattern.title}을 활용해 ${payload.targetCustomer}가 바로 공감하는 문제 상황을 열고, ${payload.productName}의 핵심 혜택을 해결 루틴처럼 제안하는 ${payload.tone} 캠페인입니다.`,
    instagramCaption: `${hook}\n카페, 배달, 택시, 구독료까지 조금씩 나갔는데 합치면 꽤 큽니다.\n${payload.productName}로 월급이 사라지기 전에 ${payload.keyBenefit}을 먼저 챙겨보세요.\n가입 전 ${payload.eligibility} 및 ${payload.caution}은 꼭 확인하세요.`,
    youtubeShortsScript: [
      `0-3초: “${hook}”라는 자막과 함께 통장 잔액을 확인하는 장면`,
      `4-7초: 반복 소비 항목이 빠르게 쌓이며 “조금씩 나갔는데 왜 이렇게 크지?”를 보여줌`,
      `8-12초: ${payload.productName}의 ${payload.keyBenefit}을 월급 루틴으로 소개`,
      '13-15초: “조건 확인하고 내 돈관리 루틴부터 시작” CTA 노출',
    ],
    tiktokCopy: `${hook} ${payload.productName}로 돈관리 루틴을 먼저 잠가두는 방법. 조건과 유의사항은 꼭 확인!`,
    cardNewsCopies: [
      `${hook}`,
      '작은 소비가 쌓이면 월급은 생각보다 빨리 사라집니다.',
      `${payload.productName}: ${payload.keyBenefit}`,
      `가입 조건: ${payload.eligibility}`,
      `시작 전 체크: ${payload.caution}`,
    ],
    hashtags: ['#월급관리', '#MZ재테크', '#금융루틴', '#소비공감', `#${payload.productType}`],
    cta: `${payload.productName} 조건 확인하고 내 캠페인 랜딩으로 이동하기`,
    abTests: buildABTests(payload),
  }
}

export async function mockCheckCompliance(payload: ComplianceInput): Promise<ComplianceResult> {
  await delay(500)

  const issues: ComplianceIssue[] = [
    {
      text: payload.generatedTexts.find((text) => text.includes('월급')) ?? '월급이 사라지기 전에 자동저축부터.',
      riskType: '과도한 불안 조성 표현',
      severity: '보통',
      reason: '문제 제기는 효과적이지만 “사라진다”는 표현은 불안을 강하게 자극할 수 있습니다.',
      revision: '“월급을 쓰기 전에 자동저축 루틴을 먼저 설정해보세요.”',
    },
    {
      text: payload.eligibility,
      riskType: '가입조건 누락 여부',
      severity: payload.eligibility ? '낮음' : '높음',
      reason: payload.eligibility ? '가입 대상과 조건이 함께 제시되어 오해 가능성이 낮습니다.' : '가입 조건이 없으면 누구나 가입 가능한 것처럼 보일 수 있습니다.',
      revision: payload.eligibility || '가입 대상, 우대 조건, 제한 조건을 본문 또는 하단 고지에 추가하세요.',
    },
    {
      text: payload.productCaution,
      riskType: '금융상품 주의사항 누락 여부',
      severity: payload.productCaution ? '낮음' : '높음',
      reason: payload.productCaution ? '주의사항이 광고 본문에 포함되어 있습니다.' : '중도해지, 수수료, 우대 조건 등 중요 유의사항이 빠져 있습니다.',
      revision: payload.productCaution || '상품 설명서 확인, 중도해지 시 혜택 변동 가능성 등을 함께 표기하세요.',
    },
  ]

  const riskLevel = issues.some((issue) => issue.severity === '높음') ? '높음' : issues.some((issue) => issue.severity === '보통') ? '보통' : '낮음'

  return {
    riskLevel,
    issues,
    finalRecommendation: '밈 표현은 유지하되 단정적 표현을 줄이고, 가입 조건과 유의사항을 CTA 근처에 함께 배치하는 것을 권장합니다.',
  }
}
