from uuid import UUID

from sqlalchemy import select
from sqlalchemy import func
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

    def search_similar(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        distance = DocumentChunk.embedding.cosine_distance(embedding)

        statement = (
            select(DocumentChunk, distance)
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        )

        return list(self.db.execute(statement).all())

    def search_full_text(
        self,
        query: str,
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        search_query = func.plainto_tsquery("english", query)

        rank = func.ts_rank_cd(
            DocumentChunk.search_vector,
            search_query,
        )

        statement = (
            select(DocumentChunk, rank)
            .where(
                DocumentChunk.search_vector.op("@@")(search_query)
            )
            .order_by(rank.desc())
            .limit(limit)
        )

        return list(self.db.execute(statement).all())