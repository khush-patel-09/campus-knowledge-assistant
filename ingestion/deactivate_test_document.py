from sqlalchemy import select

from backend.app.db.session import SessionLocal
from backend.app.models import Document


def main() -> None:
    with SessionLocal() as db:
        documents = db.scalars(
            select(Document).where(
                Document.title == "Test Document",
                Document.is_active.is_(True),
            )
        ).all()

        if not documents:
            print("No active Test Document record found.")
            return

        for document in documents:
            document.is_active = False
            print(f"Deactivated: {document.title} ({document.id})")

        db.commit()
        print("Cleanup complete.")


if __name__ == "__main__":
    main()