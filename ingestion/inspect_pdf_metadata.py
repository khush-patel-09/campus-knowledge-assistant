from pathlib import Path

from ingestion.src.loaders.pdf import PDFLoader


def main() -> None:
    source = Path("ingestion/data/raw/cse_syllabus.pdf")
    loader = PDFLoader()

    pages = loader.load_pages(source)

    print(f"Pages extracted: {len(pages)}")

    for page_number, text in pages[:5]:
        print(f"\n--- Page {page_number} ---")
        print(text[:500])


if __name__ == "__main__":
    main()