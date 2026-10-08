from dataclasses import dataclass

from backend.app.db.repositories import DocumentChunkRepository
from backend.app.models import DocumentChunk
from backend.app.services import EmbeddingService


@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    score: float
    source: str = "unknown"

@dataclass
class RetrievalFilters:
    department: str | None = None
    academic_year: str | None = None
    document_type: str | None = None


class RetrievalService:
    def __init__(
        self,
        chunk_repository: DocumentChunkRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self.chunk_repository = chunk_repository
        self.embedding_service = embedding_service

    def search(
        self,
        query: str,
        limit: int = 5,
        filters: RetrievalFilters | None = None,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            return []

        query_embedding = self.embedding_service.embed_texts([query])[0]

        filters = filters or RetrievalFilters()

        results = self.chunk_repository.search_similar(
            embedding=query_embedding,
            limit=limit,
            department=filters.department,
            academic_year=filters.academic_year,
            document_type=filters.document_type,
        )

        return [
            RetrievedChunk(
                chunk=chunk,
                score=1.0 - distance,
                source="vector",
            )
            for chunk, distance in results
        ]

    def keyword_search(
        self,
        query: str,
        limit: int = 5,
        filters: RetrievalFilters | None = None,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            return []

        results = self.chunk_repository.search_full_text(
            query=query,
            limit=limit,
        )

        filters = filters or RetrievalFilters()

        results = self.chunk_repository.search_full_text(
            query=query,
            limit=limit,
            department=filters.department,
            academic_year=filters.academic_year,
            document_type=filters.document_type,
        )

        return [
            RetrievedChunk(
                chunk=chunk,
                score=score,
                source="full_text",
            )
            for chunk, score in results
        ]

    def hybrid_search(
        self,
        query: str,
        limit: int = 5,
        candidate_limit: int = 10,
        rrf_k: int = 60,
        filters: RetrievalFilters | None = None,
    ) -> list[RetrievedChunk]:

        filters = filters or RetrievalFilters()

        vector_results = self.search(
            query=query,
            limit=candidate_limit,
            filters=filters,
        )

        keyword_results = self.keyword_search(
            query=query,
            limit=candidate_limit,
            filters=filters,
        )
        
        if not query.strip():
            return []

        vector_results = self.search(
            query=query,
            limit=candidate_limit,
        )

        keyword_results = self.keyword_search(
            query=query,
            limit=candidate_limit,
        )

        scores: dict[str, float] = {}
        chunks: dict[str, DocumentChunk] = {}

        for rank, result in enumerate(vector_results, start=1):
            chunk_id = str(result.chunk.id)

            scores[chunk_id] = scores.get(chunk_id, 0.0) + (
                1.0 / (rrf_k + rank)
            )
            chunks[chunk_id] = result.chunk

        for rank, result in enumerate(keyword_results, start=1):
            chunk_id = str(result.chunk.id)

            scores[chunk_id] = scores.get(chunk_id, 0.0) + (
                1.0 / (rrf_k + rank)
            )
            chunks[chunk_id] = result.chunk

        ranked_ids = sorted(
            scores,
            key=scores.get,
            reverse=True,
        )[:limit]

        return [
            RetrievedChunk(
                chunk=chunks[chunk_id],
                score=scores[chunk_id],
                source="hybrid",
            )
            for chunk_id in ranked_ids
        ]