
import json
from unittest.mock import MagicMock, patch

from evaluation.metrics.faithfulness_eval import FaithfulnessEvaluator


@patch("evaluation.metrics.faithfulness_eval.chat")
def test_evaluator_calculates_faithfulness(mock_chat):
    mock_response = MagicMock()
    mock_response.message.content = json.dumps({
        "claims": [
            {
                "claim": "CS 101 is an introductory programming course.",
                "verdict": "supported",
                "evidence": "CS 101 - Introduction to Computer Programming.",
            },
            {
                "claim": "CS 154 is a database course.",
                "verdict": "unsupported",
                "evidence": "",
            },
            {
                "claim": "CS 296 involves programming.",
                "verdict": "partially_supported",
                "evidence": "Programming in AWK and Java.",
            },
        ]
    })

    mock_chat.return_value = mock_response

    evaluator = FaithfulnessEvaluator()

    result = evaluator.evaluate(
        answer="CS 101, CS 154 and CS 296 are listed courses.",
        context="CS 101 - Introduction to Computer Programming.",
    )

    assert result["total_claims"] == 3
    assert result["supported_claims"] == 1
    assert result["partially_supported_claims"] == 1
    assert result["unsupported_claims"] == 1
    assert result["faithfulness_score"] == 1 / 3


def test_evaluator_handles_empty_answer():
    evaluator = FaithfulnessEvaluator()

    result = evaluator.evaluate(
        answer="",
        context="Some university document content.",
    )

    assert result["total_claims"] == 0
    assert result["faithfulness_score"] is None


@patch("evaluation.metrics.faithfulness_eval.chat")
def test_evaluator_rejects_invalid_verdict(mock_chat):
    mock_response = MagicMock()
    mock_response.message.content = json.dumps({
        "claims": [
            {
                "claim": "CS 101 is a programming course.",
                "verdict": "maybe",
                "evidence": "Some context.",
            }
        ]
    })

    mock_chat.return_value = mock_response

    evaluator = FaithfulnessEvaluator()

    try:
        evaluator.evaluate(
            answer="CS 101 is a programming course.",
            context="CS 101 - Introduction to Computer Programming.",
        )
        assert False, "Expected invalid evaluator output to raise an error."
    except RuntimeError:
        pass
