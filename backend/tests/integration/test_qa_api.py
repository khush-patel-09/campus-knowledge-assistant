from types import SimpleNamespace
from unittest.mock import Mock

from fastapi.testclient import TestClient

from backend.app.api.routes.qa import get_rag_pipeline
from backend.app.main import app
from backend.app.services import RAGPipeline


def test_ask_endpoint_returns_answer_and_sources():
    pipeline = Mock(spec=RAGPipeline)

    pipeline.answer_question.return_value = SimpleNamespace(
        answer="The library closes at 10:00 PM [1].",
        sources=[
            SimpleNamespace(
                reference=1,
                title="Student Handbook",
                page_number=12,
                section_title="Library Hours",
                source_url="https://example.edu/handbook",
            )
        ],
        retrieved_chunks=[],
    )

    app.dependency_overrides[get_rag_pipeline] = lambda: pipeline

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/ask",
            json={
                "question": "When does the library close?",
                "department": "Computer Science",
                "academic_year": "2026",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["answer"] == (
            "The library closes at 10:00 PM [1]."
        )
        assert len(data["sources"]) == 1
        assert data["sources"][0]["title"] == "Student Handbook"
        assert data["sources"][0]["page_number"] == 12
        assert data["sources"][0]["reference"] == 1

        pipeline.answer_question.assert_called_once()

        call_kwargs = pipeline.answer_question.call_args.kwargs

        assert call_kwargs["question"] == (
            "When does the library close?"
        )
        assert call_kwargs["filters"].department == "Computer Science"
        assert call_kwargs["filters"].academic_year == "2026"

    finally:
        app.dependency_overrides.pop(get_rag_pipeline, None)


def test_ask_endpoint_rejects_missing_question():
    client = TestClient(app)

    response = client.post(
        "/api/v1/ask",
        json={},
    )

    assert response.status_code == 422


def test_ask_endpoint_rejects_empty_question():
    client = TestClient(app)

    response = client.post(
        "/api/v1/ask",
        json={"question": ""},
    )

    assert response.status_code == 422