def build_compliance_prompt(generated_creative_plan: dict, product_caution: str, eligibility: str) -> str:
    return f"""
Compliance / 금융광고 심의

생성된 creative plan 전체를 금융광고와 저작권 안전 관점에서 점검한다.

점검 기준:
- 금융상품 수익 보장 표현
- 누구나 가입 가능처럼 보이는 표현
- 가입조건 누락
- 우대금리 조건 누락
- 원본 YouTube 영상 문구/구성/썸네일/음악을 과도하게 모방하는 위험
- 특정 세대 조롱 표현
- 과도한 불안 조성 표현
- 금융소비자 오인 가능성

creativePlan:
{generated_creative_plan}

productCaution: {product_caution}
eligibility: {eligibility}

JSON만 출력:
{{
  "riskLevel": "low | medium | high",
  "issues": [
    {{
      "text": "...",
      "riskType": "...",
      "severity": "low | medium | high",
      "reason": "...",
      "revision": "..."
    }}
  ],
  "finalRecommendation": "...",
  "copyrightSafetyRecommendation": "...",
  "financialAdSafetyRecommendation": "..."
}}
"""
