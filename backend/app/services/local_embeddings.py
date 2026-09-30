from sentence_transformers import SentenceTransformer

from backend.app.services.embeddings import EmbeddingService


class LocalEmbeddingService(EmbeddingService):
    def __init__(self) -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()