from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import logging

from fastapi import HTTPException

from backend.app.api.dependencies import get_db
from backend.app.core.rag import create_rag_pipeline
from backend.app.schemas.qa import (
    AskRequest,
    AskResponse,
    SourceResponse,
)
from backend.app.services import RAGPipeline, RetrievalFilters

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Question Answering"])


def get_rag_pipeline(
    db: Session = Depends(get_db),
) -> RAGPipeline:
    return create_rag_pipeline(db)


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

    try:
        result = pipeline.answer_question(
            question=request.question,
            filters=filters,
        )
    except Exception as exc:
        logger.exception("Question answering failed")
        raise HTTPException(
            status_code=503,
            detail="The question answering service is temporarily unavailable.",
        ) from exc

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