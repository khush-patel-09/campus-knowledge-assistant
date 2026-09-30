from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import DocumentChunk


class DocumentChunkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_document_id(
        self,
        document_id: UUID,
    ) -> list[DocumentChunk]:
        statement = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(self.db.scalars(statement).all())

    def create_many(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:
        self.db.add_all(chunks)
        self.db.flush()

        for chunk in chunks:
            self.db.refresh(chunk)

        return chunks