import hashlib
import math
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

SERVICE_DIR = Path(__file__).resolve().parent
load_dotenv(SERVICE_DIR.parent / ".env")
load_dotenv(SERVICE_DIR.parent.parent / ".env")

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
MOCK_EMBEDDING_DIMENSIONS = 256


def _use_mock_embedding() -> bool:
    return os.getenv("USE_MOCK_EMBEDDINGS", os.getenv("USE_MOCK_LLM", "true")).lower() == "true"


def embedding_model_name() -> str:
    return os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


def _mock_embedding(text: str) -> list[float]:
    vector = [0.0] * MOCK_EMBEDDING_DIMENSIONS
    tokens = [token.strip().lower() for token in text.replace("\n", " ").split() if token.strip()]
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % MOCK_EMBEDDING_DIMENSIONS
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def create_text_embedding(text: str) -> list[float]:
    api_key = os.getenv("OPENAI_API_KEY")
    if _use_mock_embedding() or not api_key:
        return _mock_embedding(text)

    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(
        model=embedding_model_name(),
        input=text,
    )
    return response.data[0].embedding
