import json
from typing import Dict, List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings


class SimpleRAGRetriever:
    """
    Lightweight local RAG retriever using TF-IDF.

    This avoids external API dependencies and is suitable for a capstone prototype.
    For production, replace this with embeddings + FAISS.
    """

    def __init__(self):
        self.chunks: List[Dict] = []
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None
        self._load()

    def _load(self) -> None:
        if not settings.CHUNKS_FILE.exists():
            self.chunks = []
            self.matrix = None
            return

        with open(settings.CHUNKS_FILE, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        texts = [chunk["text"] for chunk in self.chunks]

        if texts:
            self.matrix = self.vectorizer.fit_transform(texts)

    def reload(self) -> None:
        self._load()

    def search(
        self,
        query: str,
        top_k: int = settings.TOP_K,
        policy_type: Optional[str] = None,
    ) -> List[Dict]:
        if not self.chunks or self.matrix is None:
            return []

        candidate_indexes = list(range(len(self.chunks)))

        if policy_type:
            candidate_indexes = [
                index
                for index, chunk in enumerate(self.chunks)
                if chunk.get("policy_type", "").lower() == policy_type.lower()
            ]

        if not candidate_indexes:
            candidate_indexes = list(range(len(self.chunks)))

        query_vector = self.vectorizer.transform([query])
        candidate_matrix = self.matrix[candidate_indexes]
        scores = cosine_similarity(query_vector, candidate_matrix).flatten()

        ranked = sorted(
            zip(candidate_indexes, scores),
            key=lambda item: item[1],
            reverse=True,
        )[:top_k]

        results = []

        for index, score in ranked:
            chunk = self.chunks[index]
            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "document": chunk["document"],
                    "policy_type": chunk["policy_type"],
                    "text": chunk["text"],
                    "score": float(score),
                }
            )

        return results


rag_retriever = SimpleRAGRetriever()