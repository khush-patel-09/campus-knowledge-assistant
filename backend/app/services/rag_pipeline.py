from dataclasses import dataclass

from backend.app.services.generation import (
    AnswerGenerator,
    CitationSource,
)
from backend.app.services.reranker import RerankerService
from backend.app.services.retrieval import (
    RetrievedChunk,
    RetrievalFilters,
    RetrievalService,
)


@dataclass
class RAGResponse:
    answer: str
    sources: list[CitationSource]
    retrieved_chunks: list[RetrievedChunk]


class RAGPipeline:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        reranker_service: RerankerService,
        answer_generator: AnswerGenerator,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.reranker_service = reranker_service
        self.answer_generator = answer_generator

    def answer_question(
        self,
        question: str,
        filters: RetrievalFilters | None = None,
        candidate_limit: int = 10,
        final_limit: int = 5,
    ) -> RAGResponse:
        if not question.strip():
            return RAGResponse(
                answer="",
                sources=[],
                retrieved_chunks=[],
            )

        candidates = self.retrieval_service.hybrid_search(
            query=question,
            limit=candidate_limit,
            candidate_limit=candidate_limit,
            filters=filters,
        )

        reranked = self.reranker_service.rerank(
            query=question,
            results=candidates,
            limit=final_limit,
        )

        if not reranked:
            answer = self.answer_generator.generate(
                question=question,
                context="",
            )

            return RAGResponse(
                answer=answer,
                sources=[],
                retrieved_chunks=[],
            )

        sources: list[CitationSource] = []
        context_parts: list[str] = []
        source_references: dict[tuple[str, int | None, str | None], int] = {}

        for result in reranked:
            chunk = result.chunk
            document = chunk.document

            document_id = str(document.id)

            # Group chunks by document, page, and section.
            # If page metadata is unavailable, fall back to document-level citations.
            if chunk.page_number is not None:
                source_key = (
                    document_id,
                    chunk.page_number,
                    chunk.section_title,
                )
            else:
                source_key = (document_id, None, None)

            if source_key not in source_references:
                reference = len(sources) + 1
                source_references[source_key] = reference

                sources.append(
                    CitationSource(
                        reference=reference,
                        title=document.title,
                        page_number=chunk.page_number,
                        section_title=chunk.section_title,
                        source_url=document.source_url,
                    )
                )

            reference = source_references[source_key]

            context_parts.append(
                f"[{reference}]\n{chunk.content}"
            )

        context = "\n\n".join(context_parts)

        answer = self.answer_generator.generate(
            question=question,
            context=context,
            sources=sources,
        )

        return RAGResponse(
            answer=answer,
            sources=sources,
            retrieved_chunks=reranked,
        )