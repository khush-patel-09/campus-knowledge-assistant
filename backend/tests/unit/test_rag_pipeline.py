from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from backend.app.services import (
    AnswerGenerator,
    CitationSource,
    RAGPipeline,
    RetrievalService,
    RerankerService,
)


def make_retrieved_chunk(
    title: str = "Student Handbook",
    content: str = "The library closes at 10:00 PM.",
    page_number: int = 12,
    section_title: str = "Library Hours",
):
    document = SimpleNamespace(
        title=title,
        source_url="https://example.edu/handbook",
    )

    chunk = SimpleNamespace(
        id=uuid4(),
        content=content,
        page_number=page_number,
        section_title=section_title,
        document=document,
    )

    return SimpleNamespace(
        chunk=chunk,
        score=0.9,
        source="hybrid",
    )


def test_pipeline_generates_answer_with_real_source_metadata():
    retrieval = Mock(spec=RetrievalService)
    reranker = Mock(spec=RerankerService)
    generator = Mock(spec=AnswerGenerator)

    candidate = make_retrieved_chunk()

    retrieval.hybrid_search.return_value = [candidate]
    reranker.rerank.return_value = [candidate]
    generator.generate.return_value = (
        "The library closes at 10:00 PM [1]."
    )

    pipeline = RAGPipeline(
        retrieval_service=retrieval,
        reranker_service=reranker,
        answer_generator=generator,
    )

    response = pipeline.answer_question(
        question="When does the library close?"
    )

    assert response.answer == (
        "The library closes at 10:00 PM [1]."
    )
    assert len(response.sources) == 1
    assert response.sources[0].title == "Student Handbook"
    assert response.sources[0].page_number == 12
    assert response.sources[0].section_title == "Library Hours"
    assert response.sources[0].source_url == (
        "https://example.edu/handbook"
    )
    assert response.retrieved_chunks == [candidate]

    retrieval.hybrid_search.assert_called_once()
    reranker.rerank.assert_called_once()
    generator.generate.assert_called_once()

    generation_kwargs = generator.generate.call_args.kwargs
    assert "The library closes at 10:00 PM." in (
        generation_kwargs["context"]
    )
    assert generation_kwargs["sources"][0].reference == 1


def test_pipeline_returns_fallback_when_no_chunks_are_found():
    retrieval = Mock(spec=RetrievalService)
    reranker = Mock(spec=RerankerService)
    generator = Mock(spec=AnswerGenerator)

    retrieval.hybrid_search.return_value = []
    reranker.rerank.return_value = []
    generator.generate.return_value = (
        "I don't know based on the available documents."
    )

    pipeline = RAGPipeline(
        retrieval_service=retrieval,
        reranker_service=reranker,
        answer_generator=generator,
    )

    response = pipeline.answer_question(
        question="Who is the university chancellor?"
    )

    assert response.answer == (
        "I don't know based on the available documents."
    )
    assert response.sources == []
    assert response.retrieved_chunks == []

    generator.generate.assert_called_once_with(
        question="Who is the university chancellor?",
        context="",
    )


def test_pipeline_handles_empty_question():
    retrieval = Mock(spec=RetrievalService)
    reranker = Mock(spec=RerankerService)
    generator = Mock(spec=AnswerGenerator)

    pipeline = RAGPipeline(
        retrieval_service=retrieval,
        reranker_service=reranker,
        answer_generator=generator,
    )

    response = pipeline.answer_question("   ")

    assert response.answer == ""
    assert response.sources == []
    assert response.retrieved_chunks == []

    retrieval.hybrid_search.assert_not_called()
    reranker.rerank.assert_not_called()
    generator.generate.assert_not_called()