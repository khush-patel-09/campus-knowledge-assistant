import hashlib
from pathlib import Path

from backend.app.core.config import settings
from backend.app.db.repositories import DocumentChunkRepository
from backend.app.db.session import SessionLocal
from backend.app.services import LocalEmbeddingService
from backend.app.services.ingestion import IngestionService
from ingestion.src import IngestionPipeline
from ingestion.src.chunking import TextChunker
from ingestion.src.loaders import PDFLoader


RAW_DIR = Path("ingestion/data/raw")

DOCUMENTS = [
    {
        "filename": "academic_regulations.pdf",
        "title": "Academic Regulations",
        "document_type": "academic_regulations",
        "department": None,
        "academic_year": None,
    },
    {
        "filename": "cse_syllabus.pdf",
        "title": "CSE Syllabus",
        "document_type": "syllabus",
        "department": "Computer Science and Engineering",
        "academic_year": None,
    },
    {
        "filename": "student_guidelines.pdf",
        "title": "Student Guidelines",
        "document_type": "student_guidelines",
        "department": None,
        "academic_year": None,
    },
]


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def main() -> None:
    loader = PDFLoader()
    chunker = TextChunker()
    embedding_service = LocalEmbeddingService()

    pipeline = IngestionPipeline(
        loader=loader,
        chunker=chunker,
        embedding_service=embedding_service,
    )

    with SessionLocal() as db:
        ingestion_service = IngestionService(
            db=db,
            pipeline=pipeline,
        )

        for item in DOCUMENTS:
            path = RAW_DIR / item["filename"]

            if not path.is_file():
                print(f"Missing file: {path}")
                continue

            document_id = ingestion_service.ingest_document(
                source=path,
                title=item["title"],
                document_type=item["document_type"],
                content_hash=calculate_sha256(path),
                department=item["department"],
                academic_year=item["academic_year"],
            )

            print(f"Ingested: {item['title']}")
            print(f"Document ID: {document_id}")
            print()

    print("University document ingestion finished.")


if __name__ == "__main__":
    main()