import type {
  ComplianceResult,
  CampaignStudioStreamEvent,
  CampaignStudioStreamRequest,
  CollectYouTubeTrendsRequest,
  CreativeComplianceInput,
  CreativePlanResult,
  CreativePlanningRequest,
  LatestShortsAnalysisResult,
  TrendVideoPatternResult,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export function toApiAssetUrl(path?: string) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('data:')) return path
  return `${API_BASE_URL}${path}`
}

async function readErrorMessage(response: Response) {
  const text = await response.text()
  if (!text) return `API 요청에 실패했습니다. (${response.status})`

  try {
    const parsed = JSON.parse(text) as { detail?: string; message?: string }
    return parsed.detail ?? parsed.message ?? text
  } catch {
    return text
  }
}

async function postJson<TResponse>(path: string, payload: unknown): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const message = await readErrorMessage(response)
    throw new Error(`API 요청에 실패했습니다. (${response.status}) ${message}`)
  }

  return response.json() as Promise<TResponse>
}

async function getJson<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`)

  if (!response.ok) {
    const message = await readErrorMessage(response)
    throw new Error(`API 요청에 실패했습니다. (${response.status}) ${message}`)
  }

  return response.json() as Promise<TResponse>
}

export function getTrendVideoPatterns() {
  return getJson<TrendVideoPatternResult[]>('/api/trend-video-patterns')
}

export function getDefaultYouTubeKeywords() {
  return getJson<string[]>('/api/youtube/default-keywords')
}

export function collectYouTubeTrends(payload: CollectYouTubeTrendsRequest) {
  return postJson<LatestShortsAnalysisResult>('/api/youtube/collect-trends', payload)
}

export function generateCreativePlan(payload: CreativePlanningRequest) {
  return postJson<CreativePlanResult>('/api/creative-plan', payload)
}

export function checkCreativeCompliance(payload: CreativeComplianceInput) {
  return postJson<ComplianceResult>('/api/creative-compliance-check', payload)
}

export async function streamCampaignStudio(
  payload: CampaignStudioStreamRequest,
  onEvent: (event: CampaignStudioStreamEvent) => void,
) {
  const response = await fetch(`${API_BASE_URL}/api/campaign-studio/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok || !response.body) {
    const message = await readErrorMessage(response)
    throw new Error(`API 요청에 실패했습니다. (${response.status}) ${message}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue
      onEvent(JSON.parse(trimmed) as CampaignStudioStreamEvent)
    }
  }

  const trailing = buffer.trim()
  if (trailing) {
    onEvent(JSON.parse(trailing) as CampaignStudioStreamEvent)
  }
}
