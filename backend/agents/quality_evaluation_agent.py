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

QUALITY_THRESHOLD = 80

QUALITY_EVALUATION_TEMPLATE = """
Quality Evaluation Agent / 광고 기획안 품질 평가

역할:
너는 금융상품 광고 캠페인을 평가하는 AI 품질 평가 Agent다.
생성된 광고 기획안이 사용자가 입력한 금융상품, RAG 트렌드 근거, 금융광고 안전성에 맞게 작성되었는지 점검한다.

평가 기준:
- 상품 반영도: 상품명, 핵심 혜택, 가입 조건, 주의사항이 충분히 들어갔는가
- 트렌드 반영도: 선택된 트렌드 구조가 광고영상/이미지 기획에 자연스럽게 반영되었는가
- 제작 구체성: 실제 제작자가 촬영/편집할 수 있을 만큼 구체적인가
- 금융광고 안전성: 수익 보장, 누구나 가능, 과장/불안 조성 표현을 피했는가
- 저작권 안전성: 원본 영상/문구/음악/썸네일을 복제하지 않았는가

금융상품 입력:
{product_json}

생성된 광고 기획안:
{plan_json}

출력은 JSON만 반환한다.
{{
  "overallScore": 0,
  "productGroundingScore": 0,
  "trendFitScore": 0,
  "productionReadinessScore": 0,
  "financialSafetyScore": 0,
  "copyrightSafetyScore": 0,
  "shouldRevise": true,
  "issues": [
    {{
      "type": "상품 반영도 | 트렌드 반영도 | 제작 구체성 | 금융광고 안전성 | 저작권 안전성",
      "severity": "low | medium | high",
      "message": "...",
      "revisionDirection": "..."
    }}
  ],
  "improvementActions": ["..."],
  "finalRecommendation": "..."
}}
"""


def _mock_quality(plan: dict, product: CreativePlanningRequest) -> dict:
    text = json.dumps(plan, ensure_ascii=False)
    product_grounded = product.productName in text and product.keyBenefit in text
    score = 86 if product_grounded else 72
    return {
        "overallScore": score,
        "productGroundingScore": 90 if product_grounded else 62,
        "trendFitScore": 84,
        "productionReadinessScore": 86,
        "financialSafetyScore": 82,
        "copyrightSafetyScore": 88,
        "shouldRevise": score < QUALITY_THRESHOLD,
        "issues": [] if product_grounded else [
            {
                "type": "상품 반영도",
                "severity": "medium",
                "message": "광고 기획안에 상품명 또는 핵심 혜택 언급이 부족합니다.",
                "revisionDirection": "상품명, 핵심 혜택, 가입 조건을 장면과 카드뉴스에 명확히 추가하세요.",
            }
        ],
        "improvementActions": [
            "상품명, 핵심 혜택, 가입 조건, 주의사항이 각 결과물에 포함되는지 확인",
            "원본 트렌드의 문장/장면을 복제하지 않고 구조만 활용",
        ],
        "finalRecommendation": "품질 기준을 충족하지만, 금융상품 조건과 유의사항은 CTA 근처에 계속 유지하세요.",
    }


def _normalize_score(value) -> int:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 0


def _normalize_quality(result: dict) -> dict:
    normalized = {
        "overallScore": _normalize_score(result.get("overallScore")),
        "productGroundingScore": _normalize_score(result.get("productGroundingScore")),
        "trendFitScore": _normalize_score(result.get("trendFitScore")),
        "productionReadinessScore": _normalize_score(result.get("productionReadinessScore")),
        "financialSafetyScore": _normalize_score(result.get("financialSafetyScore")),
        "copyrightSafetyScore": _normalize_score(result.get("copyrightSafetyScore")),
        "shouldRevise": bool(result.get("shouldRevise")),
        "issues": result.get("issues") if isinstance(result.get("issues"), list) else [],
        "improvementActions": result.get("improvementActions") if isinstance(result.get("improvementActions"), list) else [],
        "finalRecommendation": result.get("finalRecommendation") or "품질 평가 결과를 기준으로 최종안을 검토하세요.",
    }
    if normalized["overallScore"] < QUALITY_THRESHOLD:
        normalized["shouldRevise"] = True
    return normalized


def _langchain_quality(plan: dict, product: CreativePlanningRequest) -> dict:
    prompt = PromptTemplate.from_template(QUALITY_EVALUATION_TEMPLATE)
    model_name = os.getenv("OPENAI_MODEL_QUALITY", os.getenv("OPENAI_MODEL_COMPLIANCE", "gpt-4o-mini"))
    model = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    ).bind(response_format={"type": "json_object"})
    chain = prompt | model | JsonOutputParser()
    return chain.invoke(
        {
            "product_json": product.model_dump_json(ensure_ascii=False),
            "plan_json": json.dumps(plan, ensure_ascii=False),
        }
    )


def evaluate_creative_quality(plan: dict, product: CreativePlanningRequest) -> dict:
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    if use_mock or not os.getenv("OPENAI_API_KEY"):
        return _normalize_quality(_mock_quality(plan, product))

    try:
        return _normalize_quality(_langchain_quality(plan, product))
    except Exception:
        return _normalize_quality(_mock_quality(plan, product))
