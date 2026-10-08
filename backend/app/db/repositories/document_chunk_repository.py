from uuid import UUID

from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models import Document, DocumentChunk
from collections.abc import Sequence


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

    def search_similar(
        self,
        embedding: list[float],
        limit: int = 5,
        department: str | None = None,
        academic_year: str | None = None,
        document_type: str | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        distance = DocumentChunk.embedding.cosine_distance(embedding)

        filters = [
            DocumentChunk.embedding.is_not(None),
            Document.is_active.is_(True),
        ]

        if department is not None:
            filters.append(Document.department == department)

        if academic_year is not None:
            filters.append(Document.academic_year == academic_year)

        if document_type is not None:
            filters.append(Document.document_type == document_type)

        statement = (
            select(DocumentChunk, distance)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(
                DocumentChunk.embedding.is_not(None),
                Document.is_active.is_(True),
            )
            .order_by(distance)
            .limit(limit)
        )

        return list(self.db.execute(statement).all())

    def search_full_text(
        self,
        query: str,
        limit: int = 5,
        department: str | None = None,
        academic_year: str | None = None,
        document_type: str | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        search_query = func.plainto_tsquery("english", query)

        rank = func.ts_rank_cd(
            DocumentChunk.search_vector,
            search_query,
        )

        filters = [
            DocumentChunk.search_vector.op("@@")(search_query),
            Document.is_active.is_(True),
        ]

        if department is not None:
            filters.append(Document.department == department)

        if academic_year is not None:
            filters.append(Document.academic_year == academic_year)

        if document_type is not None:
            filters.append(Document.document_type == document_type)

        statement = (
            select(DocumentChunk, rank)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(
                DocumentChunk.search_vector.op("@@")(search_query),
                Document.is_active.is_(True),
            )
            .order_by(rank.desc())
            .limit(limit)
        )

        return list(self.db.execute(statement).all())