from unittest.mock import MagicMock

from backend.app.services.generation import UNKNOWN_ANSWER
from backend.app.services.rag_pipeline import RAGPipeline


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