export type ProductType = '적금' | '예금' | '카드' | '대출' | '앱서비스'

export type TargetCustomer =
  | '대학생'
  | '사회초년생'
  | '직장인'
  | 'MZ세대'
  | '외국인'
  | '소상공인'

export type CampaignGoal =
  | '인지도 향상'
  | '클릭 유도'
  | '가입 전환'
  | '앱 설치'
  | '브랜드 이미지 개선'

export type AdChannel = '인스타그램 릴스' | '유튜브 쇼츠' | '틱톡' | '카드뉴스'

export type Tone = '공감형' | '밈 기반' | '정보형' | '신뢰형' | '위트형'

export interface CampaignFormData {
  productName: string
  productType: string
  targetCustomer: string
  keyBenefit: string
  eligibility: string
  cautions: string
  goal: string
  channel: string
  tone: string
}

export interface CampaignInput {
  productName: string
  productType: ProductType
  targetCustomer: TargetCustomer
  keyBenefit: string
  eligibility: string
  caution: string
  campaignGoal: CampaignGoal
  channels: AdChannel[]
  tone: Tone
  selectedTrendPattern: TrendPattern
}

export interface TrendPattern {
  id: string
  title: string
  description: string
  tags: string[]
}

export type RiskLevel = '낮음' | '보통' | '높음'

export interface ABTestIdea {
  variant: 'A안' | 'B안' | 'C안'
  title: string
  hook: string
  message: string
  expectedReaction: string
  channel: string
  strength: string
  caution: string
}

export interface GeneratedAdResult {
  concept: string
  instagramCaption: string
  youtubeShortsScript: string[]
  tiktokCopy: string
  cardNewsCopies: string[]
  hashtags: string[]
  cta: string
  abTests: ABTestIdea[]
}

export interface AssistantChatMessage {
  id: string
  role: 'assistant' | 'user'
  text: string
  createdAt: string
}

export type ComplianceSeverity = RiskLevel

export interface ComplianceIssue {
  text: string
  riskType: string
  severity: ComplianceSeverity
  reason: string
  revision: string
}

export interface ComplianceResult {
  riskLevel: RiskLevel
  issues: ComplianceIssue[]
  finalRecommendation: string
  copyrightSafetyRecommendation?: string
  financialAdSafetyRecommendation?: string
}

export interface ComplianceInput {
  generatedTexts: string[]
  productCaution: string
  eligibility: string
}

export interface CollectYouTubeTrendsRequest {
  publishedWithinDays?: number
  maxResultsPerKeyword?: number
  includeNonShorts: boolean
  analysisLimit?: number
}

export interface YouTubeShortsVideo {
  videoId: string
  videoUrl: string
  sourceUrl?: string
  sourceCode?: string
  mediaUrl?: string
  title: string
  channelTitle: string
  publishedAt?: string
  description?: string
  duration?: string
  durationSeconds?: number
  viewCount?: number
  likeCount?: number
  commentCount?: number
  thumbnailUrl?: string
  transcriptText?: string
  transcriptStatus: string
  searchKeyword?: string
  sourceType?: string
  sourceLabel?: string
  isShortsCandidate?: boolean
  shortsReason?: string
}

export interface LatestShortsAnalysisResult {
  sourceMode?: string
  keywordsUsed?: string[]
  totalCollected?: number
  totalShortsCandidates?: number
  fetchedVideoCount: number
  shortsCount: number
  videos: YouTubeShortsVideo[]
  patterns: TrendVideoPatternResult[]
}

export type TrendSourcePlatform = 'youtube' | 'instagram'

export interface TrendLabResultState {
  submittedProduct?: CreativePlanningRequest
  collectionOptions: CollectYouTubeTrendsRequest
  latestResult?: LatestShortsAnalysisResult
  creativePlan?: CreativePlanResult
  compliance?: ComplianceResult
  streamMessages: string[]
  streamedAnswer: string
  completedAt?: string
}

export interface TrendVideoPatternResult {
  id: string
  sourceChannel: string
  sourceTitle: string
  sourceUrl?: string | null
  country: string
  targetGeneration: string
  trendNames: string[]
  memeKeywords: string[]
  contentFormat: string
  hookStyle: string
  phraseStyle: string
  narrativeStructure: string
  editingStyle: string
  musicMood: string
  musicSignals?: string[]
  safeMusicDirection?: string | null
  thumbnailStyle: string
  visualStyle: string
  targetEmotions: string[]
  marketingUseCases: string[]
  suitableProductTypes: string[]
  copyrightRiskNotes: string[]
  financialAdRiskNotes: string[]
  exampleSafeHooks: string[]
  freshnessScore: number
  trendScore: number
  createdAt: string
  updatedAt: string
}

export interface CreativePlanningRequest {
  productName: string
  productType: string
  targetCustomer: string
  keyBenefit: string
  eligibility: string
  caution: string
  campaignGoal: string
  channels: string[]
  tone: string
  selectedTrendPatternId?: string
}

export interface CreativeScene {
  time: string
  visualDirection: string
  caption: string
  narration: string
  musicMood: string
  editingDirection: string
}

export interface QualityEvaluationIssue {
  type: string
  severity: 'low' | 'medium' | 'high' | string
  message: string
  revisionDirection: string
}

export interface QualityEvaluationResult {
  overallScore: number
  productGroundingScore: number
  trendFitScore: number
  productionReadinessScore: number
  financialSafetyScore: number
  copyrightSafetyScore: number
  shouldRevise: boolean
  issues: QualityEvaluationIssue[]
  improvementActions: string[]
  finalRecommendation: string
}

export interface AgentRevisionChange {
  field: string
  before: string
  after: string
  reason: string
}

export interface AgentWorkflowLog {
  step: string
  status: string
  detail?: string
}

export interface AgentWorkflowResult {
  revisionApplied: boolean
  decisionLogs: AgentWorkflowLog[]
  initialQuality: QualityEvaluationResult
  finalQuality: QualityEvaluationResult
  initialCompliance: ComplianceResult
  finalCompliance: ComplianceResult
  revisionSummary?: string
  changes: AgentRevisionChange[]
}

export interface CreativePlanResult {
  campaignConcept: string
  usedTrendPatterns: string[]
  coreMessage: string
  agentWorkflow?: AgentWorkflowResult
  ragInsights?: Array<{
    patternId?: string
    sourceTitle: string
    trendNames: string[]
    reason?: string
    semanticSimilarity?: number
    trendScore?: number
    freshnessScore?: number
    finalScore?: number
  }>
  videoCreative: {
    format: string
    duration: string
    sceneByScene: CreativeScene[]
    shootingGuide: string
    editingGuide: string
    musicGuide: string
    thumbnailCopy: string
    thumbnailDirection: string
  }
  trendAdaptationNotes?: string[]
  imageCreative: {
    instagramFeedCopy: string
    cardNewsCopies: string[]
    visualDirection: string
    layoutGuide: string
    safeImagePrompt: string
    generatedImage?: {
      url: string
      localPath?: string
      prompt: string
      model: string
      status: string
      referenceMediaUrls?: string[]
    }
  }
  adCopies: {
    instagramCaption: string
    youtubeShortsTitle: string
    tiktokCopy: string
    cta: string
    hashtags: string[]
  }
  abTests: Array<{
    name: string
    type: string
    hook: string
    message: string
    recommendedChannel: string
    strength: string
    caution: string
  }>
  copyrightSafetyNotes: string[]
  financialAdSafetyNotes: string[]
}

export interface CreativeComplianceInput {
  generatedCreativePlan: CreativePlanResult | Record<string, unknown>
  productCaution: string
  eligibility: string
}

export interface CampaignStudioStreamRequest {
  creativeRequest: CreativePlanningRequest
  trendRequest: CollectYouTubeTrendsRequest
  sourcePlatform?: 'youtube' | 'instagram'
}

export type CampaignStudioStreamEvent =
  | { type: 'status'; payload: { message: string } }
  | { type: 'trends'; payload: LatestShortsAnalysisResult }
  | { type: 'creativePlan'; payload: CreativePlanResult }
  | { type: 'compliance'; payload: ComplianceResult }
  | { type: 'done'; payload: { message: string } }
  | { type: 'error'; payload: { message: string; detail?: string } }
