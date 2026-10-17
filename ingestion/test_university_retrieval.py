from backend.app.db.repositories import DocumentChunkRepository
from backend.app.db.session import SessionLocal
from backend.app.services import (
    LocalEmbeddingService,
    RetrievalService,
)


def main() -> None:
    with SessionLocal() as db:
        repository = DocumentChunkRepository(db)
        embedding_service = LocalEmbeddingService()

        retrieval = RetrievalService(
            chunk_repository=repository,
            embedding_service=embedding_service,
        )

        questions = [
            "What academic regulations apply to students?",
            "Which subjects are included in the computer science syllabus?",
            "What guidelines should students follow?",
        ]

        for question in questions:
            print(f"\nQuestion: {question}")

            results = retrieval.hybrid_search(
                query=question,
                limit=3,
                candidate_limit=10,
            )

            if not results:
                print("No results found.")
                continue

            for index, result in enumerate(results, start=1):
                print(f"\nResult {index}")
                print(f"Document: {result.chunk.document.title}")
                print(f"Score: {result.score:.4f}")
                print(f"Content: {result.chunk.content[:300]}")


if __name__ == "__main__":
    main()