import hashlib
from pathlib import Path

from sqlalchemy import delete, select

from backend.app.db.session import SessionLocal
from backend.app.models import Document, DocumentChunk
from backend.app.services import LocalEmbeddingService
from ingestion.src.chunking import TextChunker
from ingestion.src.loaders import PDFLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOCUMENTS = [
    {
        "path": PROJECT_ROOT / "ingestion/data/raw/academic_regulations.pdf",
        "title": "Academic Regulations",
    },
    {
        "path": PROJECT_ROOT / "ingestion/data/raw/cse_syllabus.pdf",
        "title": "CSE Syllabus",
    },
    {
        "path": PROJECT_ROOT / "ingestion/data/raw/student_guidelines.pdf",
        "title": "Student Guidelines",
    },
]


def calculate_hash(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def main() -> None:
    loader = PDFLoader()
    chunker = TextChunker()
    embedding_service = LocalEmbeddingService()
    db = SessionLocal()

    try:
        for item in DOCUMENTS:
            path = item["path"]

            if not path.exists():
                raise FileNotFoundError(f"PDF not found: {path}")

            content_hash = calculate_hash(path)

            document = db.scalar(
                select(Document).where(
                    Document.content_hash == content_hash
                )
            )

            if document is None:
                raise ValueError(
                    f"No existing document matches {path.name} "
                    "by content hash. No chunks were replaced."
                )

            print(f"\nProcessing: {document.title}")

            page_chunks = []

            for page_number, page_text in loader.load_pages(path):
                for chunk_text in chunker.chunk(page_text):
                    page_chunks.append((chunk_text, page_number))

            if not page_chunks:
                raise ValueError(
                    f"No text chunks extracted from {path.name}"
                )

            texts = [text for text, _ in page_chunks]
            embeddings = embedding_service.embed_texts(texts)

            if len(texts) != len(embeddings):
                raise ValueError(
                    f"Embedding count mismatch for {path.name}"
                )

            if any(len(vector) != 384 for vector in embeddings):
                raise ValueError(
                    f"Unexpected embedding dimensions for {path.name}"
                )

            # Replace chunks only after extraction and embedding succeed.
            db.execute(
                delete(DocumentChunk).where(
                    DocumentChunk.document_id == document.id
                )
            )

            new_chunks = [
                DocumentChunk(
                    document_id=document.id,
                    content=text,
                    chunk_index=index,
                    page_number=page_number,
                    embedding=embedding,
                )
                for index, ((text, page_number), embedding)
                in enumerate(zip(page_chunks, embeddings))
            ]

            db.add_all(new_chunks)
            db.flush()

            print(f"Prepared {len(new_chunks)} chunks")

        # All three documents are updated in a single transaction.
        db.commit()
        print("\nBackfill completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()