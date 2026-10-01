from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.db.repositories import (
    DocumentChunkRepository,
    DocumentRepository,
)
from backend.app.models import Document, DocumentChunk
from ingestion.src import IngestionPipeline


class IngestionService:
    def __init__(
        self,
        db: Session,
        pipeline: IngestionPipeline,
    ) -> None:
        self.db = db
        self.pipeline = pipeline
        self.document_repository = DocumentRepository(db)
        self.chunk_repository = DocumentChunkRepository(db)

    def ingest_document(
        self,
        source: Path,
        title: str,
        document_type: str,
        content_hash: str,
        department: str | None = None,
        academic_year: str | None = None,
        source_url: str | None = None,
    ) -> UUID:
        existing_document = self.document_repository.get_by_content_hash(
            content_hash
        )

        if existing_document is not None:
            return existing_document.id

        document = Document(
            title=title,
            document_type=document_type,
            department=department,
            academic_year=academic_year,
            source_url=source_url,
            content_hash=content_hash,
        )

        self.document_repository.create(document)

        ingested_chunks = self.pipeline.process(source)

        chunks = [
            DocumentChunk(
                document_id=document.id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                embedding=chunk.embedding,
            )
            for chunk in ingested_chunks
        ]

        if chunks:
            self.chunk_repository.create_many(chunks)

        self.db.commit()

        return document.id