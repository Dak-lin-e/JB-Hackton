def build_performance_prompt(ad_variants: list[dict]) -> str:
    return f"""
Performance Agent

광고안별 예상 또는 실제 성과 데이터를 분석하고 다음 캠페인 전략을 제안한다.
JSON만 출력한다.

adVariants:
{ad_variants}
"""
