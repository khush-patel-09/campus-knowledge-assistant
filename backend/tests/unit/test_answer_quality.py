from types import SimpleNamespace

from evaluation.metrics.answer_quality import (
    evaluate_citation_validity,
    extract_citation_references,
)


def test_extracts_unique_citation_references():
    answer = "CS 101 [1] and CS 154 [2]. CS 467 [1]."

    assert extract_citation_references(answer) == {1, 2}


def test_accepts_valid_citations():
    sources = [
        SimpleNamespace(reference=1),
        SimpleNamespace(reference=2),
    ]

    result = evaluate_citation_validity(
        "CS 101 is listed [1].",
        sources,
    )

    assert result["citation_valid"] is True
    assert result["invalid_references"] == []
    assert result["citation_coverage"] == 1.0


def test_detects_invalid_citations():
    sources = [
        SimpleNamespace(reference=1),
    ]

    result = evaluate_citation_validity(
        "CS 101 is listed [1], and CS 154 is listed [7].",
        sources,
    )

    assert result["citation_valid"] is False
    assert result["invalid_references"] == [7]
    assert result["citation_coverage"] == 0.5


def test_handles_answers_without_citations():
    result = evaluate_citation_validity(
        "The syllabus contains programming courses.",
        [],
    )

    assert result["citation_valid"] is True
    assert result["cited_references"] == []
    assert result["citation_coverage"] is None