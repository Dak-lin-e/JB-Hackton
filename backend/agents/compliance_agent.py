import json
import os

from prompts.compliance_prompt import build_compliance_prompt
from services.llm_client import call_llm


def _fallback_compliance(generated_creative_plan: dict, product_caution: str, eligibility: str) -> dict:
    issues = [
        {
            "text": eligibility or "가입 조건 미입력",
            "riskType": "가입조건 누락",
            "severity": "low" if eligibility else "high",
            "reason": "가입 조건이 제공되었습니다." if eligibility else "누구나 가입 가능한 것처럼 오해될 수 있습니다.",
            "revision": eligibility or "가입 대상과 우대 조건을 명확히 추가하세요.",
        },
        {
            "text": product_caution or "주의사항 미입력",
            "riskType": "주의사항 누락",
            "severity": "low" if product_caution else "high",
            "reason": "주의사항이 제공되었습니다." if product_caution else "금융소비자 오인 가능성이 있습니다.",
            "revision": product_caution or "중도해지, 수수료, 우대 조건 등 유의사항을 표기하세요.",
        },
        {
            "text": str(generated_creative_plan.get("copyrightSafetyNotes", "")),
            "riskType": "저작권 모방 위험",
            "severity": "low",
            "reason": "원본 복제 금지 메모가 포함되어 있습니다.",
            "revision": "원본 문구, 음악, 썸네일 구도는 사용하지 않습니다.",
        },
    ]
    risk_level = "high" if any(item["severity"] == "high" for item in issues) else "medium"
    return {
        "riskLevel": risk_level,
        "issues": issues,
        "finalRecommendation": "가입 조건, 유의사항, 저작권 안전 메모를 함께 배치하세요.",
        "copyrightSafetyRecommendation": "원본 영상의 구체 문장/음악/썸네일을 복제하지 말고 추상 패턴만 활용하세요.",
        "financialAdSafetyRecommendation": "혜택은 조건부로 안내하고 금융소비자 오인 가능성을 줄이세요.",
    }


def _normalize_severity(value: str | None) -> str:
    if value in ("high", "높음"):
        return "높음"
    if value in ("medium", "보통"):
        return "보통"
    return "낮음"


def _normalize_compliance(result: dict) -> dict:
    issues = result.get("issues") if isinstance(result.get("issues"), list) else []
    normalized_issues = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        normalized_issues.append(
            {
                **issue,
                "severity": _normalize_severity(issue.get("severity")),
            }
        )

    risk_level = _normalize_severity(result.get("riskLevel"))
    if any(issue["severity"] == "높음" for issue in normalized_issues):
        risk_level = "높음"
    elif any(issue["severity"] == "보통" for issue in normalized_issues) and risk_level == "낮음":
        risk_level = "보통"

    return {
        **result,
        "riskLevel": risk_level,
        "issues": normalized_issues,
        "finalRecommendation": result.get("finalRecommendation") or "광고 집행 전 가입 조건과 유의사항을 함께 확인하세요.",
    }


def check_creative_compliance(generated_creative_plan: dict, product_caution: str, eligibility: str) -> dict:
    prompt = build_compliance_prompt(generated_creative_plan, product_caution, eligibility)
    try:
        return _normalize_compliance(json.loads(call_llm(prompt, model=os.getenv("OPENAI_MODEL_COMPLIANCE"))))
    except json.JSONDecodeError:
        return _normalize_compliance(_fallback_compliance(generated_creative_plan, product_caution, eligibility))
