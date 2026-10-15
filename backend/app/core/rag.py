from functools import lru_cache

from sqlalchemy.orm import Session

from backend.app.db.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from backend.app.services import (
    AnswerGenerator,
    LocalEmbeddingService,
    RAGPipeline,
    RerankerService,
    RetrievalService,
)


@lru_cache(maxsize=1)
def get_embedding_service() -> LocalEmbeddingService:
    return LocalEmbeddingService()


@lru_cache(maxsize=1)
def get_reranker_service() -> RerankerService:
    return RerankerService()


@lru_cache(maxsize=1)
def get_answer_generator() -> AnswerGenerator:
    return AnswerGenerator()


def create_rag_pipeline(db: Session) -> RAGPipeline:
    repository = DocumentChunkRepository(db)

    retrieval_service = RetrievalService(
        chunk_repository=repository,
        embedding_service=get_embedding_service(),
    )

    return RAGPipeline(
        retrieval_service=retrieval_service,
        reranker_service=get_reranker_service(),
        answer_generator=get_answer_generator(),
    )