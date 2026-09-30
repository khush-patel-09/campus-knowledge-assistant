from dataclasses import dataclass
from pathlib import Path

from ingestion.src.chunking import TextChunker
from ingestion.src.loaders import PDFLoader
from backend.app.services import EmbeddingService


@dataclass
class IngestedChunk:
    content: str
    embedding: list[float]
    chunk_index: int


class IngestionPipeline:
    def __init__(
        self,
        loader: PDFLoader,
        chunker: TextChunker,
        embedding_service: EmbeddingService,
    ) -> None:
        self.loader = loader
        self.chunker = chunker
        self.embedding_service = embedding_service

    def process(self, source: Path) -> list[IngestedChunk]:
        text = self.loader.load(source)
        chunks = self.chunker.chunk(text)

        if not chunks:
            return []

        embeddings = self.embedding_service.embed_texts(chunks)

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Embedding count does not match chunk count"
            )

        return [
            IngestedChunk(
                content=content,
                embedding=embedding,
                chunk_index=index,
            )
            for index, (content, embedding) in enumerate(
                zip(chunks, embeddings)
            )
        ]