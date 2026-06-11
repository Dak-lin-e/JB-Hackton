import copy
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from schemas import CreativePlanningRequest

AGENT_DIR = Path(__file__).resolve().parent
load_dotenv(AGENT_DIR.parent / ".env")
load_dotenv(AGENT_DIR.parent.parent / ".env")

REVISION_TEMPLATE = """
Revision Agent / 광고 기획안 자동 수정

역할:
너는 금융상품 광고 기획안을 수정하는 AI Revision Agent다.
초안의 구조는 최대한 유지하되 품질 평가 결과와 금융광고 리스크 점검 결과를 반영해 더 안전하고 명확한 최종안으로 고친다.

수정 원칙:
- 상품명, 핵심 혜택, 가입 조건, 주의사항을 광고영상/이미지/카피에 명확히 포함한다.
- 수익 보장, 누구나 가능, 최고/최대 과장, 과도한 불안 조성 표현은 완화한다.
- 원본 트렌드 영상의 문장, 썸네일 구도, 음악, 고유 개그 포인트는 복제하지 않는다.
- 숏폼 트렌드의 훅 타이밍, 자막 밀도, 컷 전환 리듬, 참여 구조만 추상적으로 반영한다.
- 결과는 기존 CreativePlanResult 구조를 유지한다.

금융상품 입력:
{product_json}

초안 광고 기획안:
{plan_json}

품질 평가 결과:
{quality_json}

컴플라이언스 점검 결과:
{compliance_json}

출력은 JSON만 반환한다.
{{
  "revisedCreativePlan": {{
    "campaignConcept": "...",
    "usedTrendPatterns": ["..."],
    "coreMessage": "...",
    "ragInsights": [],
    "videoCreative": {{
      "format": "...",
      "duration": "...",
      "sceneByScene": [
        {{
          "time": "...",
          "visualDirection": "...",
          "caption": "...",
          "narration": "...",
          "musicMood": "...",
          "editingDirection": "..."
        }}
      ],
      "shootingGuide": "...",
      "editingGuide": "...",
      "musicGuide": "...",
      "thumbnailCopy": "...",
      "thumbnailDirection": "..."
    }},
    "trendAdaptationNotes": ["..."],
    "imageCreative": {{
      "instagramFeedCopy": "...",
      "cardNewsCopies": ["1장...", "2장...", "3장...", "4장...", "5장..."],
      "visualDirection": "...",
      "layoutGuide": "...",
      "safeImagePrompt": "..."
    }},
    "adCopies": {{
      "instagramCaption": "...",
      "youtubeShortsTitle": "...",
      "tiktokCopy": "...",
      "cta": "...",
      "hashtags": ["..."]
    }},
    "abTests": [],
    "copyrightSafetyNotes": ["..."],
    "financialAdSafetyNotes": ["..."]
  }},
  "revisionSummary": "수정 요약",
  "changes": [
    {{
      "field": "수정 영역",
      "before": "수정 전",
      "after": "수정 후",
      "reason": "수정 이유"
    }}
  ]
}}
"""


def _copy_plan(plan: dict) -> dict:
    return copy.deepcopy(plan)


def _mock_revision(plan: dict, product: CreativePlanningRequest, quality: dict, compliance: dict) -> dict:
    revised = _copy_plan(plan)
    before_core = revised.get("coreMessage", "")
    revised["coreMessage"] = (
        f"{product.productName}의 {product.keyBenefit}을 설명하되, 가입 조건({product.eligibility})과 "
        f"주의사항({product.caution})을 함께 확인하도록 안내합니다."
    )
    revised.setdefault("financialAdSafetyNotes", [])
    revised["financialAdSafetyNotes"] = list(
        dict.fromkeys(
            [
                *revised["financialAdSafetyNotes"],
                "혜택은 조건 충족 시 제공될 수 있음을 함께 표기",
                "가입 조건과 주의사항을 CTA 근처에 병기",
            ]
        )
    )
    image = revised.setdefault("imageCreative", {})
    image["instagramFeedCopy"] = f"{product.productName}, 혜택과 조건을 함께 확인하세요."
    image["cardNewsCopies"] = [
        f"1장: {product.productName}, 내 금융 루틴에 맞을까요?",
        f"2장: 핵심 혜택 - {product.keyBenefit}",
        f"3장: 가입 조건 - {product.eligibility}",
        f"4장: 주의사항 - {product.caution}",
        "5장: 조건 확인하고 안전하게 시작하기",
    ]
    return {
        "revisedCreativePlan": revised,
        "revisionSummary": "품질 평가와 컴플라이언스 점검 결과를 반영해 상품 조건, 주의사항, 안전 표현을 강화했습니다.",
        "changes": [
            {
                "field": "coreMessage",
                "before": before_core,
                "after": revised["coreMessage"],
                "reason": "상품 혜택, 가입 조건, 주의사항을 한 문장 안에서 명확히 연결하기 위해 수정했습니다.",
            },
            {
                "field": "imageCreative.cardNewsCopies",
                "before": "기존 카드뉴스 문구",
                "after": "상품명, 핵심 혜택, 가입 조건, 주의사항, CTA 구조",
                "reason": "금융광고 오인 가능성을 줄이고 정보 전달력을 높이기 위해 수정했습니다.",
            },
        ],
    }


def _merge_missing_fields(original: dict, revised: dict) -> dict:
    merged = _copy_plan(original)
    for key, value in revised.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_missing_fields(merged[key], value)
        elif value not in (None, "", []):
            merged[key] = value
    return merged


def _langchain_revision(plan: dict, product: CreativePlanningRequest, quality: dict, compliance: dict) -> dict:
    prompt = PromptTemplate.from_template(REVISION_TEMPLATE)
    model_name = os.getenv("OPENAI_MODEL_REVISION", os.getenv("OPENAI_MODEL_CREATIVE", "gpt-4o-mini"))
    model = ChatOpenAI(
        model=model_name,
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY"),
    ).bind(response_format={"type": "json_object"})
    chain = prompt | model | JsonOutputParser()
    return chain.invoke(
        {
            "product_json": product.model_dump_json(ensure_ascii=False),
            "plan_json": json.dumps(plan, ensure_ascii=False),
            "quality_json": json.dumps(quality, ensure_ascii=False),
            "compliance_json": json.dumps(compliance, ensure_ascii=False),
        }
    )


def revise_creative_plan(plan: dict, product: CreativePlanningRequest, quality: dict, compliance: dict) -> dict:
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    if use_mock or not os.getenv("OPENAI_API_KEY"):
        revision = _mock_revision(plan, product, quality, compliance)
    else:
        try:
            revision = _langchain_revision(plan, product, quality, compliance)
        except Exception:
            revision = _mock_revision(plan, product, quality, compliance)

    revised_plan = revision.get("revisedCreativePlan") if isinstance(revision, dict) else None
    if not isinstance(revised_plan, dict):
        revision = _mock_revision(plan, product, quality, compliance)
        revised_plan = revision["revisedCreativePlan"]

    revision["revisedCreativePlan"] = _merge_missing_fields(plan, revised_plan)
    return revision
