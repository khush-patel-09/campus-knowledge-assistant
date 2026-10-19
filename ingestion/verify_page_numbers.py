from sqlalchemy import func, select

from backend.app.db.session import SessionLocal
from backend.app.models import Document, DocumentChunk


def main() -> None:
    db = SessionLocal()

    try:
        statement = (
            select(
                Document.title,
                func.count(DocumentChunk.id).label("total_chunks"),
                func.count(DocumentChunk.page_number).label("chunks_with_pages"),
            )
            .join(
                DocumentChunk,
                DocumentChunk.document_id == Document.id,
            )
            .where(
                Document.title.in_([
                    "Academic Regulations",
                    "CSE Syllabus",
                    "Student Guidelines",
                ])
            )
            .group_by(Document.title)
            .order_by(Document.title)
        )

        rows = db.execute(statement).all()

        for title, total, with_pages in rows:
            print(f"\n{title}")
            print(f"Total chunks: {total}")
            print(f"Chunks with page numbers: {with_pages}")

            if total != with_pages:
                print("WARNING: Some chunks are missing page numbers.")

    finally:
        db.close()


if __name__ == "__main__":
    main()