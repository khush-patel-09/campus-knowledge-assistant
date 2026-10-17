from sqlalchemy import func, select

from backend.app.db.session import SessionLocal
from backend.app.models import Document, DocumentChunk


def main() -> None:
    with SessionLocal() as db:
        statement = (
            select(
                Document.title,
                Document.is_active,
                func.count(DocumentChunk.id).label("chunk_count"),
            )
            .outerjoin(
                DocumentChunk,
                DocumentChunk.document_id == Document.id,
            )
            .group_by(Document.id)
            .order_by(Document.title)
        )

        results = db.execute(statement).all()

        print("\nDocuments in database:\n")

        for title, is_active, chunk_count in results:
            print(f"Title: {title}")
            print(f"Active: {is_active}")
            print(f"Chunks: {chunk_count}")
            print("-" * 40)

        total_chunks = db.scalar(
            select(func.count()).select_from(DocumentChunk)
        )

        embedded_chunks = db.scalar(
            select(func.count())
            .select_from(DocumentChunk)
            .where(DocumentChunk.embedding.is_not(None))
        )

        print(f"\nTotal chunks: {total_chunks}")
        print(f"Chunks with embeddings: {embedded_chunks}")


if __name__ == "__main__":
    main()