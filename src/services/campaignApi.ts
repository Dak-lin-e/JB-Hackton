import type { CampaignInput, ComplianceInput, ComplianceResult, GeneratedAdResult } from '../types'
import { mockCheckCompliance, mockGenerateAdCampaign } from './mockApi'

const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type RawSeverity = 'low' | 'medium' | 'high' | '낮음' | '보통' | '높음'

interface RawGenerateAdResponse {
  concept: string
  instagramCaption: string
  youtubeShortsScript: string | string[]
  tiktokCopy: string
  cardNewsCopies: string[]
  hashtags: string[]
  cta: string
  abTests?: Array<{
    variant?: 'A안' | 'B안' | 'C안'
    name?: string
    title?: string
    type?: string
    hook: string
    message: string
    expectedReaction?: string
    channel?: string
    strength?: string
    caution?: string
  }>
}

interface RawComplianceResponse {
  riskLevel: RawSeverity
  issues: Array<{
    text: string
    riskType: string
    severity: RawSeverity
    reason: string
    revision: string
  }>
  finalRecommendation: string
}

async function postJson<TResponse>(path: string, payload: unknown): Promise<TResponse> {
  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch {
    throw new Error('FastAPI 서버에 연결하지 못했습니다. http://localhost:8000 서버가 실행 중인지 확인해주세요.')
  }

  if (!response.ok) {
    const message = await response.text()
    throw new Error(`API 요청에 실패했습니다. (${response.status}) ${message}`)
  }

  return response.json() as Promise<TResponse>
}

function normalizeSeverity(severity: RawSeverity) {
  if (severity === 'high' || severity === '높음') return '높음'
  if (severity === 'medium' || severity === '보통') return '보통'
  return '낮음'
}

function normalizeAdResponse(response: RawGenerateAdResponse): GeneratedAdResult {
  return {
    concept: response.concept,
    instagramCaption: response.instagramCaption,
    youtubeShortsScript: Array.isArray(response.youtubeShortsScript)
      ? response.youtubeShortsScript
      : response.youtubeShortsScript.split('\n').filter(Boolean),
    tiktokCopy: response.tiktokCopy,
    cardNewsCopies: response.cardNewsCopies,
    hashtags: response.hashtags,
    cta: response.cta,
    abTests: (response.abTests ?? []).map((item, index) => ({
      variant: item.variant ?? (item.name as 'A안' | 'B안' | 'C안') ?? (index === 0 ? 'A안' : index === 1 ? 'B안' : 'C안'),
      title: item.title ?? item.type ?? '광고안',
      hook: item.hook,
      message: item.message,
      expectedReaction: item.expectedReaction ?? '초기 반응 데이터를 통해 검증이 필요합니다.',
      channel: item.channel ?? '인스타그램 릴스, 유튜브 쇼츠',
      strength: item.strength ?? '핵심 메시지가 짧아 숏폼 테스트에 적합합니다.',
      caution: item.caution ?? '금융광고 조건과 유의사항을 함께 표기해야 합니다.',
    })),
  }
}

function normalizeComplianceResponse(response: RawComplianceResponse): ComplianceResult {
  return {
    riskLevel: normalizeSeverity(response.riskLevel),
    issues: response.issues.map((issue) => ({
      ...issue,
      severity: normalizeSeverity(issue.severity),
    })),
    finalRecommendation: response.finalRecommendation,
  }
}

export async function generateAdCampaign(payload: CampaignInput): Promise<GeneratedAdResult> {
  if (USE_MOCK_API) return mockGenerateAdCampaign(payload)
  const response = await postJson<RawGenerateAdResponse>('/api/generate-ad', {
    ...payload,
    selectedTrendPattern: payload.selectedTrendPattern.title,
  })
  return normalizeAdResponse(response)
}

export async function checkCompliance(payload: ComplianceInput): Promise<ComplianceResult> {
  if (USE_MOCK_API) return mockCheckCompliance(payload)
  const response = await postJson<RawComplianceResponse>('/api/compliance-check', payload)
  return normalizeComplianceResponse(response)
}
