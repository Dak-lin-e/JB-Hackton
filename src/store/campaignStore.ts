import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import type {
  AssistantChatMessage,
  CampaignFormData,
  ComplianceResult,
  CreativePlanResult,
  GeneratedAdResult,
  TrendLabResultState,
  TrendSourcePlatform,
  TrendPattern,
} from '../types'

interface CampaignState {
  formData: CampaignFormData
  selectedPattern?: TrendPattern
  generatedAd?: GeneratedAdResult
  creativePlan?: CreativePlanResult
  complianceResult?: ComplianceResult
  trendLabResults: Partial<Record<TrendSourcePlatform, TrendLabResultState>>
  assistantMessages: AssistantChatMessage[]
  isGenerating: boolean
  generationError?: string
  setFormData: (data: CampaignFormData) => void
  setSelectedPattern: (pattern: TrendPattern) => void
  setGeneratedAd: (result: GeneratedAdResult) => void
  setCreativePlan: (result: CreativePlanResult) => void
  setComplianceResult: (result: ComplianceResult) => void
  setTrendLabResult: (platform: TrendSourcePlatform, result: TrendLabResultState) => void
  clearTrendLabResult: (platform: TrendSourcePlatform) => void
  addAssistantMessage: (message: AssistantChatMessage) => void
  clearAssistantMessages: () => void
  setGenerating: (isGenerating: boolean) => void
  setGenerationError: (error?: string) => void
  clearGeneratedResults: () => void
}

export const defaultCampaignForm: CampaignFormData = {
  productName: '청년 우대 적금',
  productType: '적금',
  targetCustomer: '사회초년생',
  keyBenefit: '월 30만원 자동저축, 우대금리 조건 충족 시 혜택 강화',
  eligibility: '만 19세 이상, 급여이체 또는 자동이체 조건 충족 고객',
  cautions: '중도해지 시 약정 혜택이 줄어들 수 있으며 세부 조건 확인 필요',
  goal: '가입 전환',
  channel: '인스타그램 릴스',
  tone: '공감형',
}

export const useCampaignStore = create<CampaignState>()(
  persist(
    (set) => ({
      formData: defaultCampaignForm,
      trendLabResults: {},
      assistantMessages: [
        {
          id: 'initial-assistant-message',
          role: 'assistant',
          text: '생성된 광고 결과를 기준으로 문구 수정, 톤 변경, 리스크 완화, A/B 조합을 도와드릴게요.',
          createdAt: new Date().toISOString(),
        },
      ],
      isGenerating: false,
      setFormData: (formData) => set({ formData }),
      setSelectedPattern: (selectedPattern) => set({ selectedPattern }),
      setGeneratedAd: (generatedAd) => set({ generatedAd }),
      setCreativePlan: (creativePlan) => set({ creativePlan }),
      setComplianceResult: (complianceResult) => set({ complianceResult }),
      setTrendLabResult: (platform, result) =>
        set((state) => ({
          trendLabResults: {
            ...state.trendLabResults,
            [platform]: result,
          },
        })),
      clearTrendLabResult: (platform) =>
        set((state) => {
          const nextResults = { ...state.trendLabResults }
          delete nextResults[platform]
          return { trendLabResults: nextResults }
        }),
      addAssistantMessage: (message) => set((state) => ({ assistantMessages: [...state.assistantMessages, message] })),
      clearAssistantMessages: () =>
        set({
          assistantMessages: [
            {
              id: `assistant-reset-${Date.now()}`,
              role: 'assistant',
              text: '대화 내용을 초기화했어요. 현재 저장된 광고 결과를 기준으로 다시 수정 요청을 해주세요.',
              createdAt: new Date().toISOString(),
            },
          ],
        }),
      setGenerating: (isGenerating) => set({ isGenerating }),
      setGenerationError: (generationError) => set({ generationError }),
      clearGeneratedResults: () =>
        set({ generatedAd: undefined, creativePlan: undefined, complianceResult: undefined }),
    }),
    {
      name: 'trend-to-finad-campaign',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        formData: state.formData,
        selectedPattern: state.selectedPattern,
        generatedAd: state.generatedAd,
        creativePlan: state.creativePlan,
        complianceResult: state.complianceResult,
        trendLabResults: state.trendLabResults,
        assistantMessages: state.assistantMessages,
      }),
    },
  ),
)
