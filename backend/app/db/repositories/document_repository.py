from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Document


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, document_id: UUID) -> Document | None:
        statement = select(Document).where(Document.id == document_id)
        return self.db.scalar(statement)

    def get_by_content_hash(self, content_hash: str) -> Document | None:
        statement = select(Document).where(
            Document.content_hash == content_hash
        )
        return self.db.scalar(statement)

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.flush()
        self.db.refresh(document)
        return document