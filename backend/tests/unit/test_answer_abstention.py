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