import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from agents.compliance_agent import check_creative_compliance
from agents.creative_planning_agent import generate_creative_plan
from agents.instagram_trend_agent import analyze_instagram_trends_from_apify
from agents.performance_agent import generate_performance_insight
from agents.quality_evaluation_agent import evaluate_creative_quality
from agents.revision_agent import revise_creative_plan
from agents.youtube_shorts_agent import analyze_keyword_trend_shorts_from_youtube
from schemas import (
    ComplianceCheckRequest,
    CampaignStudioStreamRequest,
    CollectYouTubeTrendsRequest,
    CreativePlanningRequest,
    GenerateAdRequest,
    LegacyComplianceCheckRequest,
    PerformanceInsightRequest,
)
from services.keyword_repository import load_default_keywords
from services.instagram_trending_langchain_client import InstagramTrendingApiError
from services.ad_image_generator import generate_ad_image_asset
from services.trend_video_repository import get_recent_trend_video_patterns
from services.youtube_data_client import YouTubeDataApiError

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(BACKEND_DIR.parent / ".env")
STATIC_DIR = BACKEND_DIR / "static"
GENERATED_IMAGE_DIR = STATIC_DIR / "generated-images"
GENERATED_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Trend-to-FinAd Agent API")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"message": "FastAPI backend is running"}


@app.get("/api/trend-video-patterns")
def list_trend_video_patterns():
    return get_recent_trend_video_patterns(limit=3)


@app.get("/api/youtube/default-keywords")
def get_default_youtube_keywords():
    return load_default_keywords()


@app.post("/api/youtube/collect-trends")
def collect_youtube_trends(request: CollectYouTubeTrendsRequest):
    try:
        return analyze_keyword_trend_shorts_from_youtube(request)
    except YouTubeDataApiError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "YouTube Data API 요청이 차단되었습니다. Google Cloud Console에서 "
                "YouTube Data API v3가 활성화되어 있는지, API 키 제한에 youtube.googleapis.com이 "
                "허용되어 있는지 확인해주세요."
            ),
        ) from exc


def _stream_event(event_type: str, payload: dict):
    return json.dumps({"type": event_type, "payload": payload}, ensure_ascii=False) + "\n"


def _should_revise(quality: dict, compliance: dict) -> bool:
    return bool(quality.get("shouldRevise")) or compliance.get("riskLevel") == "높음"


def _workflow_log(message: str, status: str = "completed", detail: str | None = None) -> dict:
    return {
        "step": message,
        "status": status,
        "detail": detail,
    }


def _attach_agent_workflow(
    plan: dict,
    initial_quality: dict,
    initial_compliance: dict,
    final_quality: dict,
    final_compliance: dict,
    revision: dict | None,
) -> dict:
    revision_applied = revision is not None
    plan["agentWorkflow"] = {
        "revisionApplied": revision_applied,
        "decisionLogs": [
            _workflow_log("판단: RAG 검색 결과와 금융상품 입력을 기반으로 광고 기획 초안을 생성했습니다."),
            _workflow_log(
                "검증: QualityEvaluationAgent가 상품 반영도, 트렌드 적합도, 제작 구체성, 안전성을 평가했습니다.",
                detail=f"초안 품질 점수 {initial_quality.get('overallScore', 0)}점",
            ),
            _workflow_log(
                "검증: Compliance Agent가 금융광고 리스크와 저작권 모방 위험을 점검했습니다.",
                detail=f"초안 리스크 {initial_compliance.get('riskLevel')}",
            ),
            _workflow_log(
                "개선: RevisionAgent가 자동 수정 루프를 실행했습니다." if revision_applied else "개선: 자동 수정이 필요하지 않아 초안을 최종안으로 확정했습니다.",
                detail=(revision or {}).get("revisionSummary") if revision_applied else "품질/리스크 기준을 통과했습니다.",
            ),
            _workflow_log(
                "재검증: 최종 광고안을 다시 평가하고 컴플라이언스 결과를 확정했습니다.",
                detail=f"최종 품질 점수 {final_quality.get('overallScore', 0)}점 · 최종 리스크 {final_compliance.get('riskLevel')}",
            ),
        ],
        "initialQuality": initial_quality,
        "finalQuality": final_quality,
        "initialCompliance": initial_compliance,
        "finalCompliance": final_compliance,
        "revisionSummary": (revision or {}).get("revisionSummary"),
        "changes": (revision or {}).get("changes", []),
    }
    return plan


@app.post("/api/campaign-studio/stream")
def campaign_studio_stream(request: CampaignStudioStreamRequest):
    def generate():
        try:
            is_instagram = request.sourcePlatform == "instagram"
            platform_name = "Instagram" if is_instagram else "YouTube"
            yield _stream_event("status", {"message": f"최신 {platform_name} 숏폼 트렌드를 수집하고 있습니다."})
            trend_request = CollectYouTubeTrendsRequest(
                **{
                    **request.trendRequest.model_dump(),
                    "analysisLimit": request.trendRequest.analysisLimit or 3,
                }
            )
            trend_result = (
                analyze_instagram_trends_from_apify(trend_request)
                if is_instagram
                else analyze_keyword_trend_shorts_from_youtube(trend_request)
            )
            yield _stream_event("trends", trend_result)

            first_pattern_id = (trend_result.get("patterns") or [{}])[0].get("id")
            creative_request = CreativePlanningRequest(
                **{
                    **request.creativeRequest.model_dump(),
                    "selectedTrendPatternId": first_pattern_id,
                }
            )

            yield _stream_event("status", {"message": "금융상품 정보를 반영해 광고영상기획안을 생성하고 있습니다."})
            plan = generate_creative_plan(creative_request)

            yield _stream_event("status", {"message": "QualityEvaluationAgent가 기획안 품질을 평가하고 있습니다."})
            initial_quality = evaluate_creative_quality(plan, creative_request)

            yield _stream_event("status", {"message": "Compliance Agent가 금융광고 리스크를 점검하고 있습니다."})
            initial_compliance = check_creative_compliance(
                plan,
                creative_request.caution,
                creative_request.eligibility,
            )

            revision = None
            final_plan = plan
            final_quality = initial_quality
            final_compliance = initial_compliance
            if _should_revise(initial_quality, initial_compliance):
                yield _stream_event("status", {"message": "RevisionAgent가 리스크와 품질 이슈를 반영해 기획안을 자동 수정하고 있습니다."})
                revision = revise_creative_plan(plan, creative_request, initial_quality, initial_compliance)
                final_plan = revision["revisedCreativePlan"]
                yield _stream_event("status", {"message": "수정된 기획안을 재평가하고 있습니다."})
                final_quality = evaluate_creative_quality(final_plan, creative_request)
                final_compliance = check_creative_compliance(
                    final_plan,
                    creative_request.caution,
                    creative_request.eligibility,
                )

            final_plan = _attach_agent_workflow(
                final_plan,
                initial_quality,
                initial_compliance,
                final_quality,
                final_compliance,
                revision,
            )

            yield _stream_event("status", {"message": "참조 미디어를 바탕으로 광고 이미지 파일을 생성하고 있습니다."})
            generated_image = generate_ad_image_asset(
                final_plan,
                creative_request.model_dump(),
                trend_result,
            )
            final_plan.setdefault("imageCreative", {})["generatedImage"] = generated_image
            yield _stream_event("creativePlan", final_plan)
            yield _stream_event("compliance", final_compliance)
            yield _stream_event("done", {"message": "광고영상기획안과 광고이미지생성기획안 생성이 완료되었습니다."})
        except InstagramTrendingApiError as exc:
            yield _stream_event(
                "error",
                {
                    "message": "Apify Instagram Trending Scraper 요청 중 문제가 발생했습니다. APIFY_API_TOKEN과 Actor 설정을 확인해주세요.",
                    "detail": str(exc),
                },
            )
        except YouTubeDataApiError as exc:
            yield _stream_event(
                "error",
                {
                    "message": (
                        "YouTube Data API 요청이 차단되었습니다. Google Cloud Console에서 "
                        "YouTube Data API v3와 API 키 제한을 확인해주세요."
                    ),
                    "detail": str(exc),
                },
            )
        except Exception as exc:
            yield _stream_event(
                "error",
                {
                    "message": "광고 기획안 생성 중 문제가 발생했습니다.",
                    "detail": str(exc),
                },
            )

    return StreamingResponse(generate(), media_type="application/x-ndjson")


@app.post("/api/creative-plan")
def creative_plan(request: CreativePlanningRequest):
    return generate_creative_plan(request)


@app.post("/api/creative-compliance-check")
def creative_compliance_check(request: ComplianceCheckRequest):
    return check_creative_compliance(
        request.generatedCreativePlan,
        request.productCaution,
        request.eligibility,
    )


@app.post("/api/generate-ad")
def generate_ad(request: GenerateAdRequest):
    creative_request = CreativePlanningRequest(
        productName=request.productName,
        productType=request.productType,
        targetCustomer=request.targetCustomer,
        keyBenefit=request.keyBenefit,
        eligibility=request.eligibility,
        caution=request.caution,
        campaignGoal=request.campaignGoal,
        channels=request.channels,
        tone=request.tone,
        selectedTrendPatternId=None,
    )
    plan = generate_creative_plan(creative_request)
    video = plan.get("videoCreative", {})
    image = plan.get("imageCreative", {})
    ad_copies = plan.get("adCopies", {})
    scene_lines = [
        f"{scene.get('time')}: {scene.get('caption')} / {scene.get('narration')}"
        for scene in video.get("sceneByScene", [])
    ]

    return {
        "concept": plan.get("campaignConcept", ""),
        "instagramCaption": ad_copies.get("instagramCaption", ""),
        "youtubeShortsScript": scene_lines,
        "tiktokCopy": ad_copies.get("tiktokCopy", ""),
        "cardNewsCopies": image.get("cardNewsCopies", []),
        "hashtags": ad_copies.get("hashtags", []),
        "cta": ad_copies.get("cta", "조건 확인하기"),
        "abTests": plan.get("abTests", []),
    }


@app.post("/api/compliance-check")
def compliance_check(request: LegacyComplianceCheckRequest):
    generated_creative_plan = {
        "legacyGeneratedTexts": request.generatedTexts,
        "financialAdSafetyNotes": [request.productCaution],
    }
    return check_creative_compliance(
        generated_creative_plan,
        request.productCaution,
        request.eligibility,
    )


@app.post("/api/performance-insight")
def performance_insight(request: PerformanceInsightRequest):
    return generate_performance_insight(request.adVariants)
