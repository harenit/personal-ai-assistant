import json
import math
from pathlib import Path
from typing import Any
from backend.config.settings import settings
from backend.rag.document_loader import DocumentLoader
from backend.rag.chunker import TextChunker
from backend.rag.embeddings import embedding_service

class LocalVectorStore:
    def __init__(self, store_file: Path = settings.VECTORSTORE_DIR / "store.json"):
        self.store_file = store_file
        self.chunks: list[dict[str, Any]] = []
        self._load()

    def _load(self):
        if self.store_file.exists():
            try:
                with open(self.store_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception:
                self.chunks = []
        else:
            self.chunks = []

    def _save(self):
        with open(self.store_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

    def add_document(self, doc_id: str, file_path: str | Path) -> int:
        """Parses, chunks, embeds and persists document chunks."""
        pages = DocumentLoader.load_file(file_path)
        chunks = TextChunker.chunk_pages(pages)

        # Remove existing chunks for this doc_id
        self.chunks = [c for c in self.chunks if c.get("doc_id") != doc_id]

        for chunk in chunks:
            vector = embedding_service.get_embedding(chunk["text"])
            self.chunks.append({
                "doc_id": doc_id,
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "source": chunk["source"],
                "page_number": chunk["page_number"],
                "vector": vector
            })

        self._save()
        return len(chunks)

    def delete_document(self, doc_id: str):
        self.chunks = [c for c in self.chunks if c.get("doc_id") != doc_id]
        self._save()

    def search(self, query: str, top_k: int = 4, doc_id: str = None) -> list[dict[str, Any]]:
        """Searches vector store using cosine similarity."""
        if not self.chunks:
            return []

        query_vec = embedding_service.get_embedding(query)
        candidates = self.chunks
        if doc_id:
            candidates = [c for c in candidates if c.get("doc_id") == doc_id]

        scored = []
        for item in candidates:
            item_vec = item.get("vector", [])
            sim = self._cosine_similarity(query_vec, item_vec)
            scored.append({
                "chunk_id": item["chunk_id"],
                "text": item["text"],
                "source": item["source"],
                "page_number": item["page_number"],
                "score": sim
            })

        # Sort descending by similarity
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 <= 0.0 or norm2 <= 0.0:
            return 0.0

        return dot / (norm1 * norm2)

vector_store = LocalVectorStore()
