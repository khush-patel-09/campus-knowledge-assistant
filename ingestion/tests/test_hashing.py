from pathlib import Path

from ingestion.src import calculate_file_hash


def test_file_hash_is_deterministic(tmp_path: Path) -> None:
    file_path = tmp_path / "document.txt"
    file_path.write_text("Campus Knowledge Assistant")

    first_hash = calculate_file_hash(file_path)
    second_hash = calculate_file_hash(file_path)

    assert first_hash == second_hash


def test_different_files_have_different_hashes(tmp_path: Path) -> None:
    first_file = tmp_path / "first.txt"
    second_file = tmp_path / "second.txt"

    first_file.write_text("Document A")
    second_file.write_text("Document B")

    assert calculate_file_hash(first_file) != calculate_file_hash(
        second_file
    )


def test_hash_is_sha256(tmp_path: Path) -> None:
    file_path = tmp_path / "document.txt"
    file_path.write_text("test")

    file_hash = calculate_file_hash(file_path)

    assert len(file_hash) == 64