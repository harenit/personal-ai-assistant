import math
import requests
from typing import Any
from backend.config.settings import settings

class EmbeddingService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_EMBED_MODEL

    def get_embedding(self, text: str) -> list[float]:
        """Fetch vector embedding from Ollama or fallback to local hashing vectorizer."""
        try:
            url = f"{self.base_url}/api/embeddings"
            response = requests.post(
                url,
                json={"model": self.model, "prompt": text},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                emb = data.get("embedding", [])
                if emb:
                    return emb
        except Exception:
            pass

        # Robust pure-Python fallback: 128-dim normalized term/char hash vector
        return self._fallback_embedding(text)

    def _fallback_embedding(self, text: str, dim: int = 128) -> list[float]:
        vec = [0.0] * dim
        words = text.lower().split()
        if not words:
            return vec

        for word in words:
            idx = abs(hash(word)) % dim
            vec[idx] += 1.0

        # Also hash bigrams for sequence awareness
        for i in range(len(words) - 1):
            bigram = f"{words[i]}_{words[i+1]}"
            idx = abs(hash(bigram)) % dim
            vec[idx] += 1.5

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

embedding_service = EmbeddingService()
