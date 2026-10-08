from sentence_transformers import CrossEncoder

from backend.app.models import DocumentChunk
from backend.app.services.retrieval import RetrievedChunk


class RerankerService:
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ) -> None:
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        results: list[RetrievedChunk],
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        if not query.strip() or not results:
            return []

        pairs = [
            (query, result.chunk.content)
            for result in results
        ]

        scores = self.model.predict(pairs)

        reranked = [
            RetrievedChunk(
                chunk=result.chunk,
                score=float(score),
                source="reranked",
            )
            for result, score in zip(results, scores)
        ]

        reranked.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return reranked[:limit]