from prompts.performance_prompt import build_performance_prompt
from services.llm_client import call_llm
import json
import os


def generate_performance_insight(ad_variants: list[dict]) -> dict:
    if not ad_variants:
        return {
            "summary": "분석할 광고안 데이터가 없습니다.",
            "bestCtrVariant": "-",
            "bestConversionVariant": "-",
            "recommendation": "광고안별 지표를 먼저 수집하세요.",
            "nextCampaignStrategy": "테스트 가능한 A/B 구조를 설계하세요.",
        }
    try:
        return json.loads(call_llm(build_performance_prompt(ad_variants), model=os.getenv("OPENAI_MODEL_PERFORMANCE")))
    except json.JSONDecodeError:
        best_ctr = max(ad_variants, key=lambda item: item.get("clicks", 0) / item.get("impressions", 1))
        best_conversion = max(ad_variants, key=lambda item: item.get("conversions", 0) / item.get("clicks", 1))
        return {
            "summary": f"{best_ctr.get('name')}은 클릭 반응이 가장 좋고, {best_conversion.get('name')}은 전환 효율이 가장 높습니다.",
            "bestCtrVariant": best_ctr.get("name"),
            "bestConversionVariant": best_conversion.get("name"),
            "recommendation": "공감형 훅과 혜택 설명 구조를 결합하세요.",
            "nextCampaignStrategy": "Before/After 구조를 추천합니다.",
        }
