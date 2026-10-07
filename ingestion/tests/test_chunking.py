from ingestion.src.chunking import TextChunker


def test_empty_text_returns_no_chunks() -> None:
    chunker = TextChunker()

    assert chunker.chunk("   ") == []


def test_text_is_split_into_multiple_chunks() -> None:
    chunker = TextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    text = "This is a test sentence. " * 50

    chunks = chunker.chunk(text)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_chunk_order_is_preserved() -> None:
    chunker = TextChunker(
        chunk_size=50,
        chunk_overlap=10,
    )

    text = "First section. " * 10 + "Second section. " * 10

    chunks = chunker.chunk(text)

    assert chunks
    assert "First" in chunks[0]