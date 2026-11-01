
import json
from pathlib import Path

from backend.app.core.rag import create_rag_pipeline
from backend.app.db.session import SessionLocal
from backend.app.services.generation import UNKNOWN_ANSWER
from evaluation.metrics.answer_quality import evaluate_citation_validity
from evaluation.metrics.faithfulness_eval import FaithfulnessEvaluator


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
        faithfulness_evaluator = FaithfulnessEvaluator()

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

            citation_metrics = evaluate_citation_validity(
                response.answer,
                response.sources,
            )

            retrieved_context = [
                {
                    "content": chunk.chunk.content,
                    "page_number": chunk.chunk.page_number,
                    "section_title": chunk.chunk.section_title,
                    "document_title": chunk.chunk.document.title,
                }
                for chunk in response.retrieved_chunks
            ]

            if not expected_abstention and retrieved_context:
                context = "\n\n".join(
                    chunk["content"]
                    for chunk in retrieved_context
                )

                faithfulness_metrics = faithfulness_evaluator.evaluate(
                    answer=response.answer,
                    context=context,
                )
            else:
                faithfulness_metrics = {
                    "claims": [],
                    "total_claims": 0,
                    "supported_claims": 0,
                    "partially_supported_claims": 0,
                    "unsupported_claims": 0,
                    "faithfulness_score": None,
                }

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
                "citation_valid": citation_metrics["citation_valid"],
                "cited_references": citation_metrics["cited_references"],
                "invalid_references": citation_metrics["invalid_references"],
                "citation_coverage": citation_metrics["citation_coverage"],
                "retrieved_context": retrieved_context,
                "faithfulness": faithfulness_metrics,
            }

            results.append(result)

            print(f"Answer: {response.answer}")
            print(f"Expected source: {expected_source}")
            print(f"Retrieved sources: {retrieved_sources}")
            print(f"Expected source found: {expected_source_found}")
            print(f"Expected abstention: {expected_abstention}")
            print(f"Actual abstention: {actual_abstention}")
            print(f"Abstention correct: {result['abstention_correct']}")
            print(f"Citation valid: {citation_metrics['citation_valid']}")
            print(f"Invalid references: {citation_metrics['invalid_references']}")
            print(
                f"Faithfulness score: "
                f"{faithfulness_metrics['faithfulness_score']}"
            )
            print(
                f"Supported claims: "
                f"{faithfulness_metrics['supported_claims']}"
            )
            print(
                f"Partially supported claims: "
                f"{faithfulness_metrics['partially_supported_claims']}"
            )
            print(
                f"Unsupported claims: "
                f"{faithfulness_metrics['unsupported_claims']}"
            )

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

    citation_cases = [
        result for result in results
        if result["cited_references"]
    ]

    valid_citations = sum(
        result["citation_valid"]
        for result in citation_cases
    )

    faithfulness_cases = [
        result["faithfulness"]
        for result in results
        if result["faithfulness"]["faithfulness_score"] is not None
    ]

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

    if citation_cases:
        citation_accuracy = (
            valid_citations / len(citation_cases) * 100
        )

        print(
            f"Citation validity: "
            f"{valid_citations}/{len(citation_cases)} "
            f"({citation_accuracy:.2f}%)"
        )

    if faithfulness_cases:
        average_faithfulness = sum(
            item["faithfulness_score"]
            for item in faithfulness_cases
        ) / len(faithfulness_cases)

        total_supported = sum(
            item["supported_claims"]
            for item in faithfulness_cases
        )

        total_partial = sum(
            item["partially_supported_claims"]
            for item in faithfulness_cases
        )

        total_unsupported = sum(
            item["unsupported_claims"]
            for item in faithfulness_cases
        )

        print(
            f"Average faithfulness: "
            f"{average_faithfulness * 100:.2f}%"
        )
        print(f"Supported claims: {total_supported}")
        print(f"Partially supported claims: {total_partial}")
        print(f"Unsupported claims: {total_unsupported}")


if __name__ == "__main__":
    evaluate()
