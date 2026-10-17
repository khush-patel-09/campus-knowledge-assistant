from unittest.mock import MagicMock, patch

from backend.app.services.generation import (
    AnswerGenerator,
    CitationSource,
    UNKNOWN_ANSWER,
)


@patch("backend.app.services.generation.chat")
def test_generator_receives_context_and_source_metadata(mock_chat):
    mock_response = MagicMock()
    mock_response.message.content = (
        "CS 101 is Introduction to Computer Programming [1]."
    )
    mock_chat.return_value = mock_response

    generator = AnswerGenerator()

    sources = [
        CitationSource(
            reference=1,
            title="CSE Syllabus",
            section_title="Programming Courses",
        )
    ]

    answer = generator.generate(
        question="Which programming course is listed?",
        context="[1]\nCS 101 - Introduction to Computer Programming.",
        sources=sources,
    )

    assert "CS 101" in answer
    assert "[1]" in answer

    call_args = mock_chat.call_args
    messages = call_args.kwargs["messages"]

    system_prompt = messages[0]["content"]
    user_prompt = messages[1]["content"]

    assert "CSE Syllabus" in system_prompt
    assert "Programming Courses" in system_prompt
    assert "CS 101" in user_prompt


def test_generator_abstains_when_context_is_empty():
    generator = AnswerGenerator()

    answer = generator.generate(
        question="What is the current market price of Bitcoin?",
        context="",
    )

    assert answer == UNKNOWN_ANSWER