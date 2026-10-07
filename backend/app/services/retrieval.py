from dataclasses import dataclass

from backend.app.db.repositories import DocumentChunkRepository
from backend.app.models import DocumentChunk
from backend.app.services import EmbeddingService


@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    score: float


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
    ) -> list[RetrievedChunk]:
        if not query.strip():
            return []

        query_embedding = self.embedding_service.embed_texts([query])[0]

        results = self.chunk_repository.search_similar(
            embedding=query_embedding,
            limit=limit,
        )

        return [
            RetrievedChunk(
                chunk=chunk,
                score=1.0 - distance,
            )
            for chunk, distance in results
        ]

    def keyword_search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            return []

        results = self.chunk_repository.search_full_text(
            query=query,
            limit=limit,
        )

        return [
            RetrievedChunk(
                chunk=chunk,
                score=score,
            )
            for chunk, score in results
        ]