import json
from pathlib import Path

from backend.app.core.rag import create_rag_pipeline
from backend.app.db.session import SessionLocal
from backend.app.services.generation import UNKNOWN_ANSWER


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "evaluation" / "datasets" / "qa_dataset.json"
RESULTS_PATH = (
    PROJECT_ROOT / "evaluation" / "experiments" / "answer_results.json"
)


def evaluate() -> None:
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not dataset:
        print("Evaluation dataset is empty.")
        return

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    results = []

    try:
        pipeline = create_rag_pipeline(db)

        for item in dataset:
            print(f"\nEvaluating {item['id']}: {item['question']}")

            response = pipeline.answer_question(
                question=item["question"],
            )

            expected_abstention = (
                item.get("category") == "unanswerable"
            )
            actual_abstention = (
                response.answer.strip() == UNKNOWN_ANSWER
            )

            retrieved_sources = [
                source.title for source in response.sources
            ]
            expected_source = item.get("expected_source")

            expected_source_found = (
                expected_source is not None
                and expected_source in retrieved_sources
            )

            result = {
                "id": item["id"],
                "question": item["question"],
                "ground_truth": item["ground_truth"],
                "generated_answer": response.answer,
                "expected_source": expected_source,
                "retrieved_sources": retrieved_sources,
                "expected_abstention": expected_abstention,
                "actual_abstention": actual_abstention,
                "abstention_correct": (
                    expected_abstention == actual_abstention
                ),
                "expected_source_found": expected_source_found,
            }

            results.append(result)

            print(f"Answer: {response.answer}")
            print(f"Expected source: {expected_source}")
            print(f"Retrieved sources: {retrieved_sources}")
            print(f"Expected source found: {expected_source_found}")
            print(f"Expected abstention: {expected_abstention}")
            print(f"Actual abstention: {actual_abstention}")
            print(f"Abstention correct: {result['abstention_correct']}")

    finally:
        db.close()

    with RESULTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    abstention_cases = [
        result for result in results
        if result["expected_abstention"]
    ]

    correct_abstentions = sum(
        result["abstention_correct"]
        for result in abstention_cases
    )

    answerable_cases = [
        result for result in results
        if not result["expected_abstention"]
    ]

    correct_sources = sum(
        result["expected_source_found"]
        for result in answerable_cases
    )

    print("\n" + "=" * 60)
    print(f"Questions evaluated: {len(results)}")
    print(f"Results saved to: {RESULTS_PATH}")

    if abstention_cases:
        abstention_accuracy = (
            correct_abstentions / len(abstention_cases) * 100
        )
        print(
            f"Abstention accuracy: "
            f"{correct_abstentions}/{len(abstention_cases)} "
            f"({abstention_accuracy:.2f}%)"
        )

    if answerable_cases:
        source_accuracy = (
            correct_sources / len(answerable_cases) * 100
        )
        print(
            f"Expected-source retrieval: "
            f"{correct_sources}/{len(answerable_cases)} "
            f"({source_accuracy:.2f}%)"
        )


if __name__ == "__main__":
    evaluate()