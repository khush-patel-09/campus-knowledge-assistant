from unittest.mock import MagicMock, patch
from backend.app.services.generation import CitationSource, validate_citations

from backend.app.services.generation import (
    AnswerGenerator,
    UNKNOWN_ANSWER,
)


def test_generator_returns_unknown_when_context_is_empty():
    generator = AnswerGenerator()

    answer = generator.generate(
        question="What is the current market price of Bitcoin?",
        context="",
    )

    assert answer == UNKNOWN_ANSWER


@patch("backend.app.services.generation.chat")
def test_generator_can_return_answer_from_context(mock_chat):
    mock_response = MagicMock()
    mock_response.message.content = (
        "CS 101 is Introduction to Computer Programming."
    )
    mock_chat.return_value = mock_response

    generator = AnswerGenerator()

    answer = generator.generate(
        question="Which programming course is listed?",
        context="[1]\nCS 101 - Introduction to Computer Programming.",
    )

    assert answer == "CS 101 is Introduction to Computer Programming."
    mock_chat.assert_called_once()

def test_citation_validator_accepts_available_references():
    sources = [
        CitationSource(reference=1, title="CSE Syllabus"),
        CitationSource(reference=2, title="Academic Regulations"),
    ]

    answer = "CS 101 is listed in the syllabus [1]. Course registration is covered in [2]."

    assert validate_citations(answer, sources)


def test_citation_validator_rejects_unknown_references():
    sources = [
        CitationSource(reference=1, title="CSE Syllabus"),
        CitationSource(reference=2, title="Academic Regulations"),
    ]

    answer = "CS 101 is listed in the syllabus [7]."

    assert not validate_citations(answer, sources)


def test_citation_validator_accepts_answers_without_citations():
    sources = [
        CitationSource(reference=1, title="CSE Syllabus"),
    ]

    assert validate_citations(
        "The syllabus contains programming courses.",
        sources,
    )


def test_citation_validator_rejects_citations_without_available_sources():
    assert not validate_citations(
        "The syllabus lists CS 101 [1].",
        [],
    )