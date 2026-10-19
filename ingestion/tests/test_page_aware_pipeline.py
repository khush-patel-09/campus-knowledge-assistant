from pathlib import Path
from unittest.mock import MagicMock

from ingestion.src.pipeline import IngestionPipeline


def test_pipeline_preserves_page_numbers():
    loader = MagicMock()
    chunker = MagicMock()
    embedding_service = MagicMock()

    loader.load_pages.return_value = [
        (1, "Page one content"),
        (2, "Page two content"),
    ]

    chunker.chunk.side_effect = [
        ["First page chunk"],
        ["Second page chunk"],
    ]

    embedding_service.embed_texts.return_value = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    pipeline = IngestionPipeline(
        loader=loader,
        chunker=chunker,
        embedding_service=embedding_service,
    )

    chunks = pipeline.process(Path("test.pdf"))

    assert len(chunks) == 2
    assert chunks[0].content == "First page chunk"
    assert chunks[0].page_number == 1
    assert chunks[1].content == "Second page chunk"
    assert chunks[1].page_number == 2
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1