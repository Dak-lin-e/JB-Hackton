import { FormEvent, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { Badge } from '../../shared/components/Badge'
import { streamCampaignStudio, toApiAssetUrl } from '../../services/api'
import { useCampaignStore } from '../../store/campaignStore'
import type {
  ComplianceResult,
  CollectYouTubeTrendsRequest,
  CreativePlanResult,
  CreativePlanningRequest,
  LatestShortsAnalysisResult,
  TrendLabResultState,
  TrendVideoPatternResult,
} from '../../types'
import { toCampaignFormData, toGeneratedAdResult, toTrendPattern } from './utils/resultStudioAdapter'

const inputClass =
  'w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100'

type TrendPlatform = 'youtube' | 'instagram'

const platformConfigs = {
  youtube: {
    badge: 'YouTube 최신 트렌드 자동 분석 Agent',
    title: '금융상품 입력만으로 광고 기획안을 생성합니다',
    description:
      '사용자가 키워드나 영상을 직접 넣지 않습니다. 금융상품 정보를 입력하면 백엔드가 내부 트렌드 키워드로 최신 YouTube 흐름을 찾고, 가능한 경우 자막을 분석해 트렌드/밈 패턴을 추출한 뒤 광고 영상 기획안, 이미지 제작 기획안, 이미지 생성용 안전 프롬프트, 광고 문구, 카드뉴스 문구를 생성합니다.',
    platformName: 'YouTube',
    contentName: '영상',
    shortFormName: 'Shorts',
    buttonText: 'YouTube 최신 트렌드 기반 광고 기획안 생성하기',
    trendDoneMessage: 'YouTube 트렌드 근거 분석이 완료되었습니다.',
    sourceLinkLabel: 'YouTube에서 보기',
    sessionKey: 'trend-to-finad-agent:youtube-campaign-form',
  },
  instagram: {
    badge: 'Instagram 최신 트렌드 자동 분석 Agent',
    title: '인스타 트렌드 문법으로 금융광고 기획안을 생성합니다',
    description:
      '사용자가 게시물이나 릴스 URL을 직접 넣지 않습니다. 금융상품 정보를 입력하면 최신 숏폼 트렌드 구조를 참고해 인스타그램 릴스/피드 중심 광고 영상 기획안, 이미지 제작 기획안, 이미지 생성용 안전 프롬프트, 광고 문구, 카드뉴스 문구를 생성합니다.',
    platformName: 'Instagram',
    contentName: '콘텐츠',
    shortFormName: 'Reels',
    buttonText: 'Instagram 최신 트렌드 기반 광고 기획안 생성하기',
    trendDoneMessage: 'Instagram 트렌드 근거 분석이 완료되었습니다.',
    sourceLinkLabel: '참조 콘텐츠 보기',
    sessionKey: 'trend-to-finad-agent:instagram-campaign-form',
  },
} satisfies Record<TrendPlatform, Record<string, string>>

const defaultCreativeForm: CreativePlanningRequest = {
  productName: '',
  productType: '',
  targetCustomer: '',
  keyBenefit: '',
  eligibility: '',
  caution: '',
  campaignGoal: '',
  channels: [],
  tone: '',
  selectedTrendPatternId: '',
}

function loadSessionForm(sessionKey: string) {
  try {
    const stored = window.sessionStorage.getItem(sessionKey)
    return stored ? { ...defaultCreativeForm, ...JSON.parse(stored) } : defaultCreativeForm
  } catch {
    return defaultCreativeForm
  }
}

function formatCreativePlanAnswer(plan: CreativePlanResult, product: CreativePlanningRequest) {
  const scenes = plan.videoCreative.sceneByScene
    .map(
      (scene) =>
        `${scene.time}\n- 화면: ${scene.visualDirection}\n- 자막: ${scene.caption}\n- 내레이션: ${scene.narration}\n- 편집: ${scene.editingDirection}`,
    )
    .join('\n\n')

  return [
    `${product.productName} 맞춤 광고 기획안입니다.`,
    '',
    '[금융상품 요약]',
    `상품 유형: ${product.productType}`,
    `타깃 고객: ${product.targetCustomer}`,
    `핵심 혜택: ${product.keyBenefit}`,
    `가입 조건: ${product.eligibility}`,
    `주의사항: ${product.caution}`,
    '',
    '[캠페인 콘셉트]',
    plan.campaignConcept,
    plan.coreMessage,
    '',
    '[트렌드 문법 반영 방식]',
    ...(plan.trendAdaptationNotes?.length
      ? plan.trendAdaptationNotes
      : ['인기 숏폼에서 반복되는 훅 타이밍, 빠른 컷 전환, 큰 자막, 참여 유도 구조를 금융상품 광고 소재로 재구성했습니다.']),
    '',
    '[광고영상기획안]',
    `포맷: ${plan.videoCreative.format}`,
    `분량: ${plan.videoCreative.duration}`,
    '',
    scenes,
    '',
    `촬영 가이드: ${plan.videoCreative.shootingGuide}`,
    `편집 가이드: ${plan.videoCreative.editingGuide}`,
    '',
    '[음악 추천]',
    plan.videoCreative.musicGuide,
    '원본 영상의 음악을 그대로 쓰지 않고, 추출된 음악 분위기와 템포만 참고해 저작권 클리어 음원을 사용합니다.',
    '',
    `썸네일 문구: ${plan.videoCreative.thumbnailCopy}`,
    `썸네일 방향: ${plan.videoCreative.thumbnailDirection}`,
    '',
    '[광고이미지생성기획안]',
    `피드 카피: ${plan.imageCreative.instagramFeedCopy}`,
    `비주얼 방향: ${plan.imageCreative.visualDirection}`,
    `레이아웃: ${plan.imageCreative.layoutGuide}`,
    '',
    plan.imageCreative.cardNewsCopies.join('\n'),
    '',
    '[이미지 생성용 안전 프롬프트]',
    plan.imageCreative.safeImagePrompt,
    '',
    '[광고 문구]',
    `인스타그램 캡션: ${plan.adCopies.instagramCaption}`,
    `쇼츠 제목: ${plan.adCopies.youtubeShortsTitle}`,
    `틱톡 카피: ${plan.adCopies.tiktokCopy}`,
    `CTA: ${plan.adCopies.cta}`,
    `해시태그: ${plan.adCopies.hashtags.join(' ')}`,
  ].join('\n')
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="text-sm font-semibold text-slate-700">{label}</span>
      <div className="mt-2">{children}</div>
    </label>
  )
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-lg font-bold text-slate-950">{title}</h2>
      <div className="mt-5">{children}</div>
    </section>
  )
}

function PatternCards({
  patterns,
  helperText,
  platformName,
}: {
  patterns: TrendVideoPatternResult[]
  helperText?: string
  platformName: string
}) {
  const visiblePatterns = patterns.slice(0, 3)

  if (!patterns.length) {
    return <p className="text-sm text-slate-500">아직 분석된 {platformName} 트렌드 패턴이 없습니다.</p>
  }

  return (
    <div>
      {helperText && <p className="mb-4 text-sm font-medium text-slate-500">{helperText}</p>}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {visiblePatterns.map((pattern) => (
          <article key={pattern.id} className="rounded-lg border border-slate-200 bg-white p-4">
            <p className="text-xs font-semibold text-cyan-700">{pattern.sourceChannel}</p>
            <h3 className="mt-2 font-bold text-slate-950">{pattern.sourceTitle}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">{pattern.contentFormat}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {pattern.trendNames.slice(0, 3).map((name) => (
                <Badge key={name}>{name}</Badge>
              ))}
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2 text-xs font-semibold">
              <p className="rounded-lg bg-cyan-50 p-2 text-cyan-700">트렌드 {pattern.trendScore}</p>
              <p className="rounded-lg bg-emerald-50 p-2 text-emerald-700">신선도 {pattern.freshnessScore}</p>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}

function CreativePlanView({ plan, product }: { plan: CreativePlanResult; product: CreativePlanningRequest }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-lg bg-slate-950 p-4 text-white">
          <p className="text-xs font-semibold text-slate-300">광고 대상 상품</p>
          <p className="mt-2 text-lg font-bold">{product.productName}</p>
          <p className="mt-1 text-sm text-slate-300">{product.productType} · {product.targetCustomer}</p>
        </div>
        <div className="rounded-lg bg-cyan-50 p-4">
          <p className="text-xs font-semibold text-cyan-700">핵심 혜택</p>
          <p className="mt-2 text-sm font-bold leading-6 text-slate-950">{product.keyBenefit}</p>
        </div>
        <div className="rounded-lg bg-emerald-50 p-4">
          <p className="text-xs font-semibold text-emerald-700">광고 목표</p>
          <p className="mt-2 text-sm font-bold leading-6 text-slate-950">{product.campaignGoal}</p>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <div className="rounded-lg border border-slate-200 p-4">
          <h3 className="font-bold text-slate-950">금융상품 설명</h3>
          <dl className="mt-3 space-y-3 text-sm leading-6">
            <div>
              <dt className="font-semibold text-slate-500">가입 조건</dt>
              <dd className="text-slate-800">{product.eligibility}</dd>
            </div>
            <div>
              <dt className="font-semibold text-slate-500">주의사항</dt>
              <dd className="text-slate-800">{product.caution}</dd>
            </div>
          </dl>
        </div>
        <div className="rounded-lg border border-slate-200 p-4">
          <h3 className="font-bold text-slate-950">트렌드 활용 방향</h3>
          <p className="mt-3 text-sm leading-6 text-slate-700">
            {plan.usedTrendPatterns.length
              ? `${plan.usedTrendPatterns.join(', ')} 구조를 참고하되, 원본 문구와 화면 구도는 복제하지 않고 ${product.productName}의 혜택과 조건을 중심으로 재구성합니다.`
              : `${product.productName}의 혜택과 가입 조건을 중심으로 숏폼 광고 구조를 설계합니다.`}
          </p>
        </div>
      </div>

      <div className="rounded-lg bg-slate-50 p-4">
        <p className="text-sm font-bold text-slate-950">캠페인 콘셉트</p>
        <p className="mt-2 text-sm leading-6 text-slate-700">{plan.campaignConcept}</p>
        <p className="mt-2 text-sm text-slate-600">{plan.coreMessage}</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <div className="rounded-lg border border-slate-200 p-4">
          <h3 className="font-bold text-slate-950">광고영상기획안</h3>
          <p className="mt-2 text-sm text-slate-600">
            {plan.videoCreative.format} · {plan.videoCreative.duration}
          </p>
          <div className="mt-4 space-y-3">
            {plan.videoCreative.sceneByScene.map((scene) => (
              <div key={scene.time} className="rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-700">
                <p className="font-bold text-slate-950">{scene.time}</p>
                <p>{scene.visualDirection}</p>
                <p>{scene.caption}</p>
                <p>{scene.narration}</p>
                <p>{scene.editingDirection}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 space-y-2 text-sm leading-6 text-slate-700">
            <p><span className="font-semibold text-slate-950">촬영 가이드:</span> {plan.videoCreative.shootingGuide}</p>
            <p><span className="font-semibold text-slate-950">편집 가이드:</span> {plan.videoCreative.editingGuide}</p>
            <p><span className="font-semibold text-slate-950">음악 가이드:</span> {plan.videoCreative.musicGuide}</p>
            <p><span className="font-semibold text-slate-950">썸네일 문구:</span> {plan.videoCreative.thumbnailCopy}</p>
            <p><span className="font-semibold text-slate-950">썸네일 방향:</span> {plan.videoCreative.thumbnailDirection}</p>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 p-4">
          <h3 className="font-bold text-slate-950">광고이미지생성기획안</h3>
          {plan.imageCreative.generatedImage?.url && (
            <div className="mt-4 overflow-hidden rounded-lg border border-slate-200 bg-slate-50">
              <img
                src={toApiAssetUrl(plan.imageCreative.generatedImage.url)}
                alt="생성된 광고 이미지 시안"
                className="aspect-square w-full object-cover"
              />
              <div className="flex items-center justify-between gap-3 p-3">
                <p className="text-xs font-semibold text-slate-500">
                  {plan.imageCreative.generatedImage.model} · {plan.imageCreative.generatedImage.status}
                </p>
                <a
                  href={toApiAssetUrl(plan.imageCreative.generatedImage.url)}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-bold text-cyan-700"
                >
                  이미지 파일 열기
                </a>
              </div>
            </div>
          )}
          <p className="mt-2 text-sm leading-6 text-slate-700">{plan.imageCreative.instagramFeedCopy}</p>
          <div className="mt-4 space-y-2 text-sm leading-6 text-slate-700">
            <p><span className="font-semibold text-slate-950">비주얼 방향:</span> {plan.imageCreative.visualDirection}</p>
            <p><span className="font-semibold text-slate-950">레이아웃:</span> {plan.imageCreative.layoutGuide}</p>
          </div>
          <ul className="mt-4 space-y-2 text-sm text-slate-600">
            {plan.imageCreative.cardNewsCopies.map((copy) => (
              <li key={copy}>{copy}</li>
            ))}
          </ul>
          <div className="mt-4 rounded-lg bg-cyan-50 p-3">
            <p className="text-xs font-bold text-cyan-700">이미지 생성용 안전 프롬프트</p>
            <p className="mt-2 text-sm leading-6 text-cyan-900">{plan.imageCreative.safeImagePrompt}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <div className="rounded-lg border border-slate-200 p-4">
          <h3 className="font-bold text-slate-950">광고 문구</h3>
          <p className="mt-3 text-sm leading-6 text-slate-700">{plan.adCopies.instagramCaption}</p>
          <p className="mt-2 text-sm text-slate-600">{plan.adCopies.tiktokCopy}</p>
          <p className="mt-2 text-sm font-semibold text-slate-950">{plan.adCopies.cta}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {plan.adCopies.hashtags.map((tag) => (
              <Badge key={tag}>{tag}</Badge>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 p-4">
          <h3 className="font-bold text-slate-950">A/B 테스트</h3>
          <div className="mt-3 space-y-3">
            {(plan.abTests ?? []).map((test) => (
              <div key={test.name} className="rounded-lg bg-slate-50 p-3 text-sm">
                <p className="font-bold text-slate-950">
                  {test.name} · {test.type}
                </p>
                <p className="mt-1 text-slate-700">{test.hook}</p>
                <p className="mt-1 text-slate-600">{test.message}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <div className="rounded-lg bg-amber-50 p-4">
          <h3 className="font-bold text-slate-950">저작권 안전 메모</h3>
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {plan.copyrightSafetyNotes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-lg bg-emerald-50 p-4">
          <h3 className="font-bold text-slate-950">금융광고 안전 메모</h3>
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {plan.financialAdSafetyNotes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

interface TrendVideoLabPageProps {
  platform?: TrendPlatform
}

export function TrendVideoLabPage({ platform = 'youtube' }: TrendVideoLabPageProps) {
  const platformConfig = platformConfigs[platform]
  const {
    trendLabResults,
    setFormData,
    setSelectedPattern,
    setGeneratedAd,
    setCreativePlan: setStoredCreativePlan,
    setComplianceResult,
    setGenerating,
    setGenerationError,
    setTrendLabResult,
    clearTrendLabResult,
    clearAssistantMessages,
    clearGeneratedResults,
  } = useCampaignStore()
  const storedLabResult = trendLabResults[platform]
  const [creativeForm, setCreativeForm] = useState<CreativePlanningRequest>(() => loadSessionForm(platformConfig.sessionKey))
  const [submittedProduct, setSubmittedProduct] = useState<CreativePlanningRequest | undefined>(() => storedLabResult?.submittedProduct)
  const [collectionOptions, setCollectionOptions] = useState<CollectYouTubeTrendsRequest>(() => storedLabResult?.collectionOptions ?? {
    publishedWithinDays: 30,
    maxResultsPerKeyword: 2,
    includeNonShorts: false,
    analysisLimit: 3,
  })
  const [latestResult, setLatestResult] = useState<LatestShortsAnalysisResult | undefined>(() => storedLabResult?.latestResult)
  const [creativePlan, setCreativePlan] = useState<CreativePlanResult | undefined>(() => storedLabResult?.creativePlan)
  const [compliance, setCompliance] = useState<ComplianceResult | undefined>(() => storedLabResult?.compliance)
  const [loading, setLoading] = useState<string>()
  const [error, setError] = useState<string>()
  const [streamMessages, setStreamMessages] = useState<string[]>(() => storedLabResult?.streamMessages ?? [])
  const [streamedAnswer, setStreamedAnswer] = useState(() => storedLabResult?.streamedAnswer ?? '')
  const answerTimerRef = useRef<number | null>(null)
  const labResultRef = useRef<TrendLabResultState>({
    submittedProduct: storedLabResult?.submittedProduct,
    collectionOptions: storedLabResult?.collectionOptions ?? collectionOptions,
    latestResult: storedLabResult?.latestResult,
    creativePlan: storedLabResult?.creativePlan,
    compliance: storedLabResult?.compliance,
    streamMessages: storedLabResult?.streamMessages ?? [],
    streamedAnswer: storedLabResult?.streamedAnswer ?? '',
    completedAt: storedLabResult?.completedAt,
  })

  const persistLabResult = (next: Partial<TrendLabResultState>) => {
    labResultRef.current = {
      ...labResultRef.current,
      ...next,
    }
    setTrendLabResult(platform, labResultRef.current)
  }

  const updateCreative = <K extends keyof CreativePlanningRequest>(key: K, value: CreativePlanningRequest[K]) => {
    setCreativeForm((prev) => {
      const next = { ...prev, [key]: value }
      window.sessionStorage.setItem(platformConfig.sessionKey, JSON.stringify(next))
      return next
    })
  }

  const streamAnswerText = (text: string) => {
    if (answerTimerRef.current) {
      window.clearInterval(answerTimerRef.current)
    }
    setStreamedAnswer('')
    let index = 0
    answerTimerRef.current = window.setInterval(() => {
      index = Math.min(index + 5, text.length)
      setStreamedAnswer(text.slice(0, index))
      if (index >= text.length && answerTimerRef.current) {
        window.clearInterval(answerTimerRef.current)
        answerTimerRef.current = null
      }
    }, 12)
  }

  const validateProduct = () => {
    if (!creativeForm.productName.trim()) return '상품명을 입력해주세요.'
    if (!creativeForm.productType.trim()) return '상품 유형을 입력해주세요.'
    if (!creativeForm.targetCustomer.trim()) return '타깃 고객을 입력해주세요.'
    if (!creativeForm.keyBenefit.trim()) return '핵심 혜택을 입력해주세요.'
    if (!creativeForm.eligibility.trim()) return '가입 조건을 입력해주세요.'
    if (!creativeForm.caution.trim()) return '주의사항을 입력해주세요.'
    if (!creativeForm.campaignGoal.trim()) return '광고 목표를 입력해주세요.'
    if (!creativeForm.channels.length) return '광고 채널을 입력해주세요.'
    if (!creativeForm.tone.trim()) return '원하는 톤을 입력해주세요.'
    return undefined
  }

  const handleGeneratePlan = async (event: FormEvent) => {
    event.preventDefault()
    setError(undefined)
    const validationError = validateProduct()
    if (validationError) {
      setError(validationError)
      return
    }

    setCreativePlan(undefined)
    setCompliance(undefined)
    setLatestResult(undefined)
    setStreamMessages([])
    setStreamedAnswer('')
    clearTrendLabResult(platform)
    labResultRef.current = {
      collectionOptions,
      streamMessages: [],
      streamedAnswer: '',
    }
    clearGeneratedResults()
    clearAssistantMessages()
    setGenerating(true)
    setGenerationError(undefined)
    const productSnapshot = { ...creativeForm }
    window.sessionStorage.setItem(platformConfig.sessionKey, JSON.stringify(productSnapshot))
    setSubmittedProduct(productSnapshot)
    persistLabResult({
      submittedProduct: productSnapshot,
      collectionOptions,
      latestResult: undefined,
      creativePlan: undefined,
      compliance: undefined,
      streamMessages: [],
      streamedAnswer: '',
    })
    setLoading('스트리밍 연결을 시작하고 있습니다...')

    try {
      await streamCampaignStudio(
        {
          creativeRequest: productSnapshot,
          trendRequest: collectionOptions,
          sourcePlatform: platform,
        },
        (event) => {
          if (event.type === 'status') {
            setLoading(event.payload.message)
            setStreamMessages((prev) => [...prev, event.payload.message])
            persistLabResult({ streamMessages: [...labResultRef.current.streamMessages, event.payload.message] })
          }
          if (event.type === 'trends') {
            setLatestResult(event.payload)
            const resultPattern = toTrendPattern(event.payload.patterns[0])
            if (resultPattern) {
              setSelectedPattern(resultPattern)
            }
            const nextMessages = [...labResultRef.current.streamMessages, platformConfig.trendDoneMessage]
            setStreamMessages((prev) => [...prev, platformConfig.trendDoneMessage])
            persistLabResult({ latestResult: event.payload, streamMessages: nextMessages })
          }
          if (event.type === 'creativePlan') {
            setCreativePlan(event.payload)
            setFormData(toCampaignFormData(productSnapshot))
            setGeneratedAd(toGeneratedAdResult(event.payload))
            setStoredCreativePlan(event.payload)
            const answerText = formatCreativePlanAnswer(event.payload, productSnapshot)
            streamAnswerText(answerText)
            const nextMessages = [...labResultRef.current.streamMessages, '광고영상기획안과 광고이미지생성기획안이 도착했습니다.']
            setStreamMessages((prev) => [...prev, '광고영상기획안과 광고이미지생성기획안이 도착했습니다.'])
            persistLabResult({ creativePlan: event.payload, streamedAnswer: answerText, streamMessages: nextMessages })
          }
          if (event.type === 'compliance') {
            setCompliance(event.payload)
            setComplianceResult(event.payload)
            const nextMessages = [...labResultRef.current.streamMessages, '금융광고 리스크 점검이 완료되었습니다.']
            setStreamMessages((prev) => [...prev, '금융광고 리스크 점검이 완료되었습니다.'])
            persistLabResult({ compliance: event.payload, streamMessages: nextMessages })
          }
          if (event.type === 'done') {
            setLoading(undefined)
            setGenerating(false)
            const nextMessages = [...labResultRef.current.streamMessages, event.payload.message]
            setStreamMessages((prev) => [...prev, event.payload.message])
            persistLabResult({ streamMessages: nextMessages, completedAt: new Date().toISOString() })
          }
          if (event.type === 'error') {
            setError(event.payload.message)
            setGenerationError(event.payload.message)
            setLoading(undefined)
            setGenerating(false)
          }
        },
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : '광고 기획안 생성 중 문제가 발생했습니다.')
      setGenerationError(err instanceof Error ? err.message : '광고 기획안 생성 중 문제가 발생했습니다.')
      setLoading(undefined)
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <Badge tone="blue">{platformConfig.badge}</Badge>
        <h2 className="mt-4 text-2xl font-bold text-slate-950">{platformConfig.title}</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">{platformConfig.description}</p>
      </section>

      {loading && <p className="rounded-lg border border-cyan-200 bg-cyan-50 p-4 text-sm font-semibold text-cyan-700">{loading}</p>}
      {error && <p className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm font-semibold text-rose-700">{error}</p>}

      <Section title="금융상품 정보 입력">
        <form onSubmit={handleGeneratePlan} className="grid gap-4 md:grid-cols-2">
          <Field label="상품명">
            <input
              className={inputClass}
              value={creativeForm.productName}
              placeholder="예: 청년 우대 적금, 여행 특화 체크카드"
              onChange={(e) => updateCreative('productName', e.target.value)}
            />
          </Field>
          <Field label="상품 유형">
            <input
              className={inputClass}
              value={creativeForm.productType}
              placeholder="예: 적금, 예금, 카드, 대출, 앱서비스"
              onChange={(e) => updateCreative('productType', e.target.value)}
            />
          </Field>
          <Field label="타깃 고객">
            <input
              className={inputClass}
              value={creativeForm.targetCustomer}
              placeholder="예: 대학생, 사회초년생, 직장인, 소상공인"
              onChange={(e) => updateCreative('targetCustomer', e.target.value)}
            />
          </Field>
          <Field label="핵심 혜택">
            <input
              className={inputClass}
              value={creativeForm.keyBenefit}
              placeholder="예: 월 최대 30만원 자동저축, 조건 충족 시 우대 혜택"
              onChange={(e) => updateCreative('keyBenefit', e.target.value)}
            />
          </Field>
          <Field label="가입 조건">
            <textarea
              className={`${inputClass} min-h-24 resize-none`}
              value={creativeForm.eligibility}
              placeholder="예: 만 19세 이상, 급여이체 또는 자동이체 조건 충족 고객"
              onChange={(e) => updateCreative('eligibility', e.target.value)}
            />
          </Field>
          <Field label="주의사항">
            <textarea
              className={`${inputClass} min-h-24 resize-none`}
              value={creativeForm.caution}
              placeholder="예: 중도해지 시 혜택 축소 가능, 상품 설명서 확인 필요"
              onChange={(e) => updateCreative('caution', e.target.value)}
            />
          </Field>
          <Field label="광고 목표">
            <input
              className={inputClass}
              value={creativeForm.campaignGoal}
              placeholder="예: 인지도 향상, 클릭 유도, 가입 전환, 앱 설치"
              onChange={(e) => updateCreative('campaignGoal', e.target.value)}
            />
          </Field>
          <Field label="채널">
            <input
              className={inputClass}
              value={creativeForm.channels.join(', ')}
              placeholder="예: 인스타그램 릴스, 유튜브 쇼츠, 틱톡"
              onChange={(e) => updateCreative('channels', e.target.value.split(',').map((item) => item.trim()).filter(Boolean))}
            />
          </Field>
          <Field label="톤">
            <input
              className={inputClass}
              value={creativeForm.tone}
              placeholder="예: 공감형, 밈 기반, 정보형, 신뢰형, 위트형"
              onChange={(e) => updateCreative('tone', e.target.value)}
            />
          </Field>
          <div className="flex items-end">
            <button type="submit" className="w-full rounded-lg bg-slate-950 px-5 py-3 text-sm font-bold text-white">
              {platformConfig.buttonText}
            </button>
          </div>

          {submittedProduct && (loading || streamedAnswer || streamMessages.length > 0) && (
            <div className="md:col-span-2 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-bold text-slate-950">AI Agent 응답</p>
                  <p className="mt-1 text-xs font-medium text-slate-500">
                    {loading ?? '광고영상기획안과 광고이미지생성기획안 생성 완료'}
                  </p>
                </div>
                <Badge tone={loading ? 'blue' : 'green'}>{loading ? '생성중' : '완료'}</Badge>
              </div>

              {streamMessages.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {streamMessages.slice(-4).map((message, index) => (
                    <Badge key={`${message}-${index}`} tone="slate">{message}</Badge>
                  ))}
                </div>
              )}

              <div className="mt-5 min-h-40 rounded-lg bg-slate-950 p-4 text-sm leading-7 text-slate-50 shadow-inner">
                {streamedAnswer ? (
                  <pre className="whitespace-pre-wrap break-words font-sans">{streamedAnswer}</pre>
                ) : (
                  <p className="text-slate-300">AI가 트렌드 근거를 확인하고 광고영상기획안과 광고이미지생성기획안을 작성하고 있습니다...</p>
                )}
              </div>
            </div>
          )}
        </form>
      </Section>

      {creativePlan && submittedProduct && (
        <Section title="생성된 광고 기획안">
          <CreativePlanView plan={creativePlan} product={submittedProduct} />
        </Section>
      )}

      {latestResult && (
        <Section title={`광고안에 반영된 ${platformConfig.platformName} 트렌드 근거`}>
          <div className="mb-4 rounded-lg border border-cyan-100 bg-cyan-50 px-4 py-3 text-sm font-semibold text-cyan-800">
            최근 {collectionOptions.publishedWithinDays}일 이내 {platformConfig.platformName} {platformConfig.contentName}에서 추출한 패턴을 광고 문구와 제작 방향에만 참고했습니다.
          </div>
          <PatternCards
            patterns={latestResult.patterns}
            platformName={platformConfig.platformName}
            helperText="아래 카드는 광고 소재가 아니라, 금융상품 광고안을 만들 때 참고한 트렌드 구조입니다."
          />
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg bg-slate-50 p-4">
              <p className="text-xs font-semibold text-slate-500">조회한 최신 {platformConfig.contentName}</p>
              <p className="mt-2 text-2xl font-bold text-slate-950">{latestResult.totalCollected ?? latestResult.fetchedVideoCount}</p>
            </div>
            <div className="rounded-lg bg-cyan-50 p-4">
              <p className="text-xs font-semibold text-cyan-700">{platformConfig.shortFormName} 후보</p>
              <p className="mt-2 text-2xl font-bold text-slate-950">{latestResult.totalShortsCandidates ?? latestResult.shortsCount}</p>
            </div>
            <div className="rounded-lg bg-emerald-50 p-4">
              <p className="text-xs font-semibold text-emerald-700">생성된 추천 패턴</p>
              <p className="mt-2 text-2xl font-bold text-slate-950">{latestResult.patterns.length}</p>
            </div>
          </div>
          <div className="mt-4 grid gap-3 lg:grid-cols-3">
            {latestResult.videos.map((video) => (
              <article key={video.videoId} className="rounded-lg border border-slate-200 p-4">
                <div className="flex flex-wrap gap-2">
                  {video.searchKeyword && <Badge tone="blue">{video.searchKeyword}</Badge>}
                  <Badge tone={video.isShortsCandidate ? 'green' : 'slate'}>{video.isShortsCandidate ? `${platformConfig.shortFormName} 후보` : '일반 후보'}</Badge>
                </div>
                <h3 className="mt-2 text-sm font-bold leading-6 text-slate-950">{video.title}</h3>
                <p className="mt-2 text-xs text-slate-500">
                  {video.channelTitle} · 길이 {video.durationSeconds ?? '-'}초 · 조회 {video.viewCount?.toLocaleString() ?? '-'}
                </p>
                <p className="mt-2 text-xs leading-5 text-slate-500">{video.shortsReason}</p>
                {video.sourceCode && <p className="mt-2 text-xs font-medium text-slate-400">코드: {video.sourceCode}</p>}
                {(video.sourceUrl || video.videoUrl) && (
                  <a
                    href={video.sourceUrl || video.videoUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-3 inline-flex text-xs font-bold text-cyan-700"
                  >
                    {platformConfig.sourceLinkLabel}
                  </a>
                )}
              </article>
            ))}
          </div>
        </Section>
      )}

      {compliance && (
        <Section title="Compliance 결과">
          <div className="space-y-3">
            {compliance.issues.map((issue) => (
              <div key={`${issue.text}-${issue.riskType}`} className="rounded-lg border border-slate-200 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-bold text-slate-950">{issue.riskType}</p>
                  <Badge tone={issue.severity === '높음' ? 'red' : issue.severity === '보통' ? 'amber' : 'green'}>{issue.severity}</Badge>
                </div>
                <p className="mt-2 text-sm text-slate-700">{issue.text}</p>
                <p className="mt-2 text-sm text-slate-500">{issue.reason}</p>
                <p className="mt-2 text-sm font-semibold text-cyan-700">{issue.revision}</p>
              </div>
            ))}
            <p className="rounded-lg bg-slate-50 p-4 text-sm font-semibold text-slate-700">{compliance.finalRecommendation}</p>
          </div>
        </Section>
      )}
    </div>
  )
}
