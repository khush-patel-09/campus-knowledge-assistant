from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db
from backend.app.db.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from backend.app.schemas.qa import (
    AskRequest,
    AskResponse,
    SourceResponse,
)
from backend.app.services import (
    AnswerGenerator,
    CitationSource,
    LocalEmbeddingService,
    RAGPipeline,
    RerankerService,
    RetrievalFilters,
    RetrievalService,
)

router = APIRouter(prefix="/api/v1", tags=["Question Answering"])


def get_rag_pipeline(
    db: Session = Depends(get_db),
) -> RAGPipeline:
    repository = DocumentChunkRepository(db)
    embedding_service = LocalEmbeddingService()
    retrieval_service = RetrievalService(
        chunk_repository=repository,
        embedding_service=embedding_service,
    )

    reranker_service = RerankerService()
    answer_generator = AnswerGenerator()

    return RAGPipeline(
        retrieval_service=retrieval_service,
        reranker_service=reranker_service,
        answer_generator=answer_generator,
    )


@router.post("/ask", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> AskResponse:
    filters = RetrievalFilters(
        department=request.department,
        academic_year=request.academic_year,
        document_type=request.document_type,
    )

    result = pipeline.answer_question(
        question=request.question,
        filters=filters,
    )

    return AskResponse(
        answer=result.answer,
        sources=[
            SourceResponse(
                reference=source.reference,
                title=source.title,
                page_number=source.page_number,
                section_title=source.section_title,
                source_url=source.source_url,
            )
            for source in result.sources
        ],
    )