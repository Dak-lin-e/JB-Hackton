import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from schemas import CreativePlanningRequest
from services.embedding_client import create_text_embedding, embedding_model_name
from services.trend_video_repository import load_trend_video_patterns, prune_stale_trend_video_patterns

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent.parent / ".runtime"
VECTOR_INDEX_FILE = Path(os.getenv("TREND_VECTOR_INDEX_FILE", DEFAULT_DATA_DIR / "trend_vector_index.json"))
DEFAULT_RAG_LIMIT = 3


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_list_text(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    return str(value or "")


def build_pattern_embedding_text(pattern: dict) -> str:
    fields = [
        f"source title: {pattern.get('sourceTitle')}",
        f"source channel: {pattern.get('sourceChannel')}",
        f"trend names: {_as_list_text(pattern.get('trendNames'))}",
        f"meme keywords: {_as_list_text(pattern.get('memeKeywords'))}",
        f"content format: {pattern.get('contentFormat')}",
        f"hook style: {pattern.get('hookStyle')}",
        f"phrase style: {pattern.get('phraseStyle')}",
        f"narrative structure: {pattern.get('narrativeStructure')}",
        f"editing style: {pattern.get('editingStyle')}",
        f"music mood: {pattern.get('musicMood')}",
        f"music signals: {_as_list_text(pattern.get('musicSignals'))}",
        f"safe music direction: {pattern.get('safeMusicDirection')}",
        f"thumbnail style: {pattern.get('thumbnailStyle')}",
        f"visual style: {pattern.get('visualStyle')}",
        f"target emotions: {_as_list_text(pattern.get('targetEmotions'))}",
        f"marketing use cases: {_as_list_text(pattern.get('marketingUseCases'))}",
        f"suitable product types: {_as_list_text(pattern.get('suitableProductTypes'))}",
        f"safe hooks: {_as_list_text(pattern.get('exampleSafeHooks'))}",
        f"financial ad risk notes: {_as_list_text(pattern.get('financialAdRiskNotes'))}",
    ]
    return "\n".join(fields)


def build_campaign_query_text(request: CreativePlanningRequest) -> str:
    return "\n".join(
        [
            f"상품명: {request.productName}",
            f"상품 유형: {request.productType}",
            f"타깃 고객: {request.targetCustomer}",
            f"핵심 혜택: {request.keyBenefit}",
            f"가입 조건: {request.eligibility}",
            f"주의사항: {request.caution}",
            f"광고 목표: {request.campaignGoal}",
            f"채널: {', '.join(request.channels)}",
            f"톤: {request.tone}",
        ]
    )


def _load_index() -> dict[str, dict]:
    if not VECTOR_INDEX_FILE.exists():
        return {}
    try:
        data = json.loads(VECTOR_INDEX_FILE.read_text(encoding="utf-8") or "{}")
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _save_index(index: dict[str, dict]) -> None:
    VECTOR_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    VECTOR_INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def _pattern_id(pattern: dict) -> str | None:
    value = pattern.get("id")
    return str(value) if value else None


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    dot = sum(left[index] * right[index] for index in range(size))
    left_norm = math.sqrt(sum(value * value for value in left[:size]))
    right_norm = math.sqrt(sum(value * value for value in right[:size]))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def upsert_trend_pattern_embedding(pattern: dict) -> None:
    pattern_id = _pattern_id(pattern)
    if not pattern_id:
        return

    text = build_pattern_embedding_text(pattern)
    index = _load_index()
    index[pattern_id] = {
        "patternId": pattern_id,
        "embedding": create_text_embedding(text),
        "embeddingText": text,
        "model": embedding_model_name(),
        "updatedAt": _now_iso(),
    }
    _save_index(index)


def upsert_trend_pattern_embeddings(patterns: list[dict]) -> None:
    for pattern in patterns:
        upsert_trend_pattern_embedding(pattern)


def _fresh_patterns_by_id() -> dict[str, dict]:
    patterns = prune_stale_trend_video_patterns(load_trend_video_patterns())
    return {str(pattern.get("id")): pattern for pattern in patterns if pattern.get("id")}


def _ensure_index_for_patterns(patterns: dict[str, dict], index: dict[str, dict]) -> dict[str, dict]:
    changed = False
    for pattern_id, pattern in patterns.items():
        if pattern_id not in index:
            text = build_pattern_embedding_text(pattern)
            index[pattern_id] = {
                "patternId": pattern_id,
                "embedding": create_text_embedding(text),
                "embeddingText": text,
                "model": embedding_model_name(),
                "updatedAt": _now_iso(),
            }
            changed = True

    stale_ids = [pattern_id for pattern_id in index if pattern_id not in patterns]
    for pattern_id in stale_ids:
        del index[pattern_id]
        changed = True

    if changed:
        _save_index(index)
    return index


def retrieve_relevant_trend_patterns(request: CreativePlanningRequest, limit: int = DEFAULT_RAG_LIMIT) -> list[dict]:
    patterns_by_id = _fresh_patterns_by_id()
    if not patterns_by_id:
        return []

    index = _ensure_index_for_patterns(patterns_by_id, _load_index())
    query_embedding = create_text_embedding(build_campaign_query_text(request))
    scored_patterns = []

    for pattern_id, item in index.items():
        pattern = patterns_by_id.get(pattern_id)
        if not pattern:
            continue
        semantic_similarity = max(0.0, _cosine_similarity(query_embedding, item.get("embedding") or []))
        trend_score = (float(pattern.get("trendScore") or 0) / 100.0)
        freshness_score = (float(pattern.get("freshnessScore") or 0) / 100.0)
        final_score = (semantic_similarity * 0.6) + (trend_score * 0.25) + (freshness_score * 0.15)
        scored_patterns.append(
            {
                **pattern,
                "rag": {
                    "semanticSimilarity": round(semantic_similarity, 4),
                    "trendScoreWeight": round(trend_score, 4),
                    "freshnessScoreWeight": round(freshness_score, 4),
                    "finalScore": round(final_score, 4),
                    "reason": (
                        f"{request.productName}, {request.productType}, {request.targetCustomer}, "
                        f"{request.keyBenefit} 조건과 의미적으로 가까운 숏폼 패턴입니다."
                    ),
                },
            }
        )

    return sorted(scored_patterns, key=lambda item: item["rag"]["finalScore"], reverse=True)[:limit]
