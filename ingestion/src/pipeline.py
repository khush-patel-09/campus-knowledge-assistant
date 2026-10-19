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
    page_number: int | None = None


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
        pages = self.loader.load_pages(source)

        page_chunks: list[tuple[str, int]] = []

        for page_number, page_text in pages:
            chunks = self.chunker.chunk(page_text)

            for chunk in chunks:
                page_chunks.append((chunk, page_number))

        if not page_chunks:
            return []

        texts = [content for content, _ in page_chunks]
        embeddings = self.embedding_service.embed_texts(texts)

        if len(texts) != len(embeddings):
            raise ValueError(
                "Embedding count does not match chunk count"
            )

        return [
            IngestedChunk(
                content=content,
                embedding=embedding,
                chunk_index=index,
                page_number=page_number,
            )
            for index, ((content, page_number), embedding) in enumerate(
                zip(page_chunks, embeddings)
            )
        ]