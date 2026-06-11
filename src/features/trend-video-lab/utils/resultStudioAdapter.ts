import type {
  ABTestIdea,
  CampaignFormData,
  CreativePlanResult,
  CreativePlanningRequest,
  GeneratedAdResult,
  TrendVideoPatternResult,
} from '../../../types'

const variants: ABTestIdea['variant'][] = ['A안', 'B안', 'C안']

export function toCampaignFormData(product: CreativePlanningRequest): CampaignFormData {
  return {
    productName: product.productName,
    productType: product.productType,
    targetCustomer: product.targetCustomer,
    keyBenefit: product.keyBenefit,
    eligibility: product.eligibility,
    cautions: product.caution,
    goal: product.campaignGoal,
    channel: product.channels.join(', '),
    tone: product.tone,
  }
}

export function toTrendPattern(pattern?: TrendVideoPatternResult) {
  if (!pattern) return undefined

  return {
    id: pattern.id,
    title: pattern.trendNames[0] ?? pattern.sourceTitle,
    description: pattern.narrativeStructure,
    tags: pattern.memeKeywords.slice(0, 4),
  }
}

export function toGeneratedAdResult(plan: CreativePlanResult): GeneratedAdResult {
  return {
    concept: `${plan.campaignConcept}\n\n${plan.coreMessage}`,
    instagramCaption: plan.adCopies.instagramCaption,
    youtubeShortsScript: [
      plan.adCopies.youtubeShortsTitle,
      ...plan.videoCreative.sceneByScene.map((scene) => `${scene.time} ${scene.caption} ${scene.narration}`),
    ],
    tiktokCopy: plan.adCopies.tiktokCopy,
    cardNewsCopies: plan.imageCreative.cardNewsCopies.slice(0, 5),
    hashtags: plan.adCopies.hashtags,
    cta: plan.adCopies.cta,
    abTests: plan.abTests.slice(0, 3).map((test, index) => ({
      variant: variants[index] ?? 'C안',
      title: `${test.name} · ${test.type}`,
      hook: test.hook,
      message: test.message,
      expectedReaction: test.type,
      channel: test.recommendedChannel,
      strength: test.strength,
      caution: test.caution,
    })),
  }
}
