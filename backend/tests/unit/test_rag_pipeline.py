from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.app.services.generation import UNKNOWN_ANSWER
from backend.app.services.rag_pipeline import RAGPipeline
from backend.app.services.retrieval import RetrievedChunk


def create_pipeline():
    retrieval_service = MagicMock()
    reranker_service = MagicMock()
    answer_generator = MagicMock()

    pipeline = RAGPipeline(
        retrieval_service=retrieval_service,
        reranker_service=reranker_service,
        answer_generator=answer_generator,
    )

    return pipeline, retrieval_service, reranker_service, answer_generator


def create_chunk(
    document_id,
    title,
    content,
    page_number=None,
    section_title=None,
):
    document = SimpleNamespace(
        id=document_id,
        title=title,
        source_url=None,
    )

    chunk = SimpleNamespace(
        id=f"chunk-{document_id}-{content[:5]}",
        content=content,
        page_number=page_number,
        section_title=section_title,
        document=document,
    )

    return RetrievedChunk(
        chunk=chunk,
        score=0.9,
        source="hybrid",
    )


def test_pipeline_returns_unknown_when_no_chunks_are_retrieved():
    pipeline, retrieval, reranker, generator = create_pipeline()

    retrieval.hybrid_search.return_value = []
    reranker.rerank.return_value = []
    generator.generate.return_value = UNKNOWN_ANSWER

    result = pipeline.answer_question(
        question="What is the current market price of Bitcoin?"
    )

    assert result.answer == UNKNOWN_ANSWER
    assert result.sources == []
    assert result.retrieved_chunks == []

    generator.generate.assert_called_once_with(
        question="What is the current market price of Bitcoin?",
        context="",
    )


def test_pipeline_returns_empty_response_for_blank_question():
    pipeline, retrieval, reranker, generator = create_pipeline()

    result = pipeline.answer_question(question="   ")

    assert result.answer == ""
    assert result.sources == []
    assert result.retrieved_chunks == []

    retrieval.hybrid_search.assert_not_called()
    reranker.rerank.assert_not_called()
    generator.generate.assert_not_called()


def test_pipeline_deduplicates_sources_from_same_document():
    pipeline, retrieval, reranker, generator = create_pipeline()

    chunks = [
        create_chunk(
            document_id="doc-1",
            title="CSE Syllabus",
            content="CS 101 - Introduction to Computer Programming.",
            page_number=1,
            section_title="Programming",
        ),
        create_chunk(
            document_id="doc-1",
            title="CSE Syllabus",
            content="CS 467 - Functional and Logic Programming.",
            page_number=2,
            section_title="Advanced Courses",
        ),
    ]

    retrieval.hybrid_search.return_value = chunks
    reranker.rerank.return_value = chunks
    generator.generate.return_value = "The courses are CS 101 and CS 467 [1]."

    result = pipeline.answer_question(
        question="Which programming courses are listed?"
    )

    assert len(result.sources) == 1
    assert result.sources[0].title == "CSE Syllabus"
    assert result.sources[0].reference == 1

    # Both chunks must remain available to the answer generator.
    generator.generate.assert_called_once()
    call_kwargs = generator.generate.call_args.kwargs

    assert "[1]" in call_kwargs["context"]
    assert "CS 101" in call_kwargs["context"]
    assert "CS 467" in call_kwargs["context"]

    # Both chunks should remain in the response.
    assert len(result.retrieved_chunks) == 2


def test_pipeline_keeps_different_documents_as_separate_sources():
    pipeline, retrieval, reranker, generator = create_pipeline()

    chunks = [
        create_chunk(
            document_id="doc-1",
            title="CSE Syllabus",
            content="CS 101 - Introduction to Computer Programming.",
        ),
        create_chunk(
            document_id="doc-2",
            title="Academic Regulations",
            content="Faculty advisors approve course registration.",
        ),
    ]

    retrieval.hybrid_search.return_value = chunks
    reranker.rerank.return_value = chunks
    generator.generate.return_value = "Answer based on both documents [1] [2]."

    result = pipeline.answer_question(
        question="Tell me about programming and registration."
    )

    assert len(result.sources) == 2
    assert result.sources[0].title == "CSE Syllabus"
    assert result.sources[1].title == "Academic Regulations"
    assert result.sources[0].reference == 1
    assert result.sources[1].reference == 2

    context = generator.generate.call_args.kwargs["context"]

    assert "[1]" in context
    assert "[2]" in context