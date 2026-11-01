import re


def extract_citation_references(answer: str) -> set[int]:
    return {
        int(reference)
        for reference in re.findall(r"\[(\d+)\]", answer)
    }


def evaluate_citation_validity(
    answer: str,
    sources: list,
) -> dict:
    cited_references = extract_citation_references(answer)

    available_references = {
        source.reference for source in sources
    }

    invalid_references = sorted(
        cited_references - available_references
    )

    return {
        "cited_references": sorted(cited_references),
        "invalid_references": invalid_references,
        "citation_valid": len(invalid_references) == 0,
        "citation_coverage": (
            len(cited_references & available_references)
            / len(cited_references)
            if cited_references else None
        ),
    }