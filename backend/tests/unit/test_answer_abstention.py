from unittest.mock import MagicMock, patch

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