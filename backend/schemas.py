from typing import Any, Optional

from pydantic import BaseModel, Field


class TrendVideoSourceRequest(BaseModel):
    videoUrl: Optional[str] = None
    videoTitle: str
    channelName: str = "YouTube"
    publishedAt: Optional[str] = None
    transcriptText: Optional[str] = None
    summaryText: str
    musicMemo: Optional[str] = None
    editingMemo: Optional[str] = None
    thumbnailMemo: Optional[str] = None
    targetGeneration: str
    category: Optional[str] = None


class CollectYouTubeTrendsRequest(BaseModel):
    publishedWithinDays: int | None = 30
    maxResultsPerKeyword: int | None = 2
    includeNonShorts: bool = False
    analysisLimit: int | None = 3


class TrendVideoPattern(BaseModel):
    id: str
    sourceChannel: str
    sourceTitle: str
    sourceUrl: Optional[str] = None
    country: str = "KR"
    targetGeneration: str
    trendNames: list[str]
    memeKeywords: list[str]
    contentFormat: str
    hookStyle: str
    phraseStyle: str
    narrativeStructure: str
    editingStyle: str
    musicMood: str
    musicSignals: list[str] = []
    safeMusicDirection: str | None = None
    thumbnailStyle: str
    visualStyle: str
    targetEmotions: list[str]
    marketingUseCases: list[str]
    suitableProductTypes: list[str]
    copyrightRiskNotes: list[str]
    financialAdRiskNotes: list[str]
    exampleSafeHooks: list[str]
    freshnessScore: int = Field(ge=0, le=100)
    trendScore: int = Field(ge=0, le=100)
    createdAt: str
    updatedAt: str


class CreativePlanningRequest(BaseModel):
    productName: str
    productType: str
    targetCustomer: str
    keyBenefit: str
    eligibility: str
    caution: str
    campaignGoal: str
    channels: list[str]
    tone: str
    selectedTrendPatternId: Optional[str] = None


class CampaignStudioStreamRequest(BaseModel):
    creativeRequest: CreativePlanningRequest
    trendRequest: CollectYouTubeTrendsRequest = Field(default_factory=CollectYouTubeTrendsRequest)
    sourcePlatform: str = "youtube"


class ComplianceCheckRequest(BaseModel):
    generatedCreativePlan: dict[str, Any]
    productCaution: str
    eligibility: str


class LegacyComplianceCheckRequest(BaseModel):
    generatedTexts: list[str]
    productCaution: str
    eligibility: str


class PerformanceInsightRequest(BaseModel):
    adVariants: list[dict[str, Any]]


class GenerateAdRequest(BaseModel):
    productName: str
    productType: str
    targetCustomer: str
    keyBenefit: str
    eligibility: str
    caution: str
    campaignGoal: str
    channels: list[str]
    tone: str
    selectedTrendPattern: str | None = None
