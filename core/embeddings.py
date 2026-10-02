"""
Embedding providers for RAG memory.

Default: LocalHashEmbedding (no external dependency)
Optional: OpenAIEmbedding when OPENAI_API_KEY is available
"""

from typing import List, Optional
import hashlib
import math
import os
import re


def _tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    return re.findall(r"[\w\u0600-\u06FF]+", text)


class BaseEmbedder:
    name = "base"

    def embed(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]


class LocalHashEmbedder(BaseEmbedder):
    """
    Lightweight deterministic embedder.
    Not semantic-SOTA, but dependency-free and stable across model switches.
    """

    name = "local_hash"

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        tokens = _tokenize(text)
        if not tokens:
            return vec

        for token in tokens:
            h = hashlib.sha256(token.encode("utf-8")).hexdigest()
            idx = int(h[:8], 16) % self.dim
            sign = 1.0 if int(h[8:10], 16) % 2 == 0 else -1.0
            vec[idx] += sign

        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class OpenAIEmbedder(BaseEmbedder):
    """Optional OpenAI embeddings provider."""

    name = "openai"

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

    def embed(self, text: str) -> List[float]:
        # Lazy import to avoid hard dependency when unused
        try:
            from openai import OpenAI
        except Exception as e:
            raise RuntimeError("openai package not installed") from e

        client = OpenAI(api_key=self.api_key)
        resp = client.embeddings.create(model=self.model, input=text)
        return list(resp.data[0].embedding)


def get_embedder(provider: Optional[str] = None) -> BaseEmbedder:
    """
    provider: local | openai | auto
    auto => openai if key exists else local
    """
    provider = (provider or os.getenv("RAMAZ_EMBEDDING_PROVIDER") or "auto").lower()

    if provider == "openai":
        return OpenAIEmbedder()

    if provider == "local":
        return LocalHashEmbedder()

    # auto
    if os.getenv("OPENAI_API_KEY"):
        try:
            return OpenAIEmbedder()
        except Exception:
            return LocalHashEmbedder()

    return LocalHashEmbedder()


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))
