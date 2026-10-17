import json
from pathlib import Path

from backend.app.services.generation import UNKNOWN_ANSWER


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "evaluation" / "datasets" / "qa_dataset.json"


def normalize(text: str) -> str:
    """Normalize text for simple exact-match evaluation."""
    return " ".join(text.lower().strip().split())


def evaluate_answers() -> None:
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not dataset:
        print("Evaluation dataset is empty.")
        return

    abstention_cases = [
        item for item in dataset
        if item.get("category") == "unanswerable"
    ]

    print("Answer Evaluation")
    print("=" * 60)
    print(f"Dataset questions: {len(dataset)}")
    print(f"Unanswerable questions: {len(abstention_cases)}")
    print()
    print(
        "This script validates evaluation references and abstention "
        "expectations. It does not call the LLM."
    )

    valid_references = 0

    for item in dataset:
        expected = item.get("ground_truth", "").strip()
        valid = bool(expected)

        if item.get("category") == "unanswerable":
            valid = valid and normalize(expected) == normalize(UNKNOWN_ANSWER)

        if valid:
            valid_references += 1

        print(
            f"{item['id']}: "
            f"{'VALID' if valid else 'CHECK REFERENCE'}"
        )

    print()
    print(f"Valid references: {valid_references}/{len(dataset)}")


if __name__ == "__main__":
    evaluate_answers()