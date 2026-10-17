import json
from pathlib import Path

from backend.app.db.repositories import DocumentChunkRepository
from backend.app.db.session import SessionLocal
from backend.app.services import LocalEmbeddingService, RetrievalService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "evaluation" / "datasets" / "qa_dataset.json"


def evaluate_retrieval(top_k: int = 5) -> None:
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not dataset:
        print("Evaluation dataset is empty.")
        return

    embedding_service = LocalEmbeddingService()
    db = SessionLocal()

    hits = 0
    reciprocal_ranks = []

    try:
        repository = DocumentChunkRepository(db)
        retrieval_service = RetrievalService(
            chunk_repository=repository,
            embedding_service=embedding_service,
        )

        print(f"\nRetrieval Evaluation (Top-{top_k})")
        print("=" * 60)

        for item in dataset:
            results = retrieval_service.hybrid_search(
                query=item["question"],
                limit=top_k,
                candidate_limit=10,
            )

            # Keep the first occurrence of each document.
            unique_sources = list(
                dict.fromkeys(
                    result.chunk.document.title
                    for result in results
                )
            )

            expected_source = item["expected_source"]

            rank = next(
                (
                    index
                    for index, title in enumerate(unique_sources, start=1)
                    if title == expected_source
                ),
                None,
            )

            if rank is not None:
                hits += 1
                reciprocal_ranks.append(1 / rank)
            else:
                reciprocal_ranks.append(0.0)

            print(f"\nQuestion: {item['question']}")
            print(f"Expected source: {expected_source}")
            print(f"Unique retrieved sources: {unique_sources}")
            print(f"Expected source rank: {rank or 'Not found'}")

        hit_rate = hits / len(dataset) * 100
        mrr = sum(reciprocal_ranks) / len(dataset)

        print("\n" + "=" * 60)
        print(f"Questions evaluated: {len(dataset)}")
        print(f"Source hits: {hits}/{len(dataset)}")
        print(f"Hit Rate@{top_k}: {hit_rate:.2f}%")
        print(f"Mean Reciprocal Rank: {mrr:.4f}")

    finally:
        db.close()


if __name__ == "__main__":
    evaluate_retrieval()