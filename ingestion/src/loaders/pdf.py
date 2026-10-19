from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from ingestion.src.loaders.base import DocumentLoader


class PDFLoader(DocumentLoader):
    def __init__(self) -> None:
        pipeline_options = PdfPipelineOptions(
            do_ocr=False,
            do_table_structure=False,
            force_backend_text=True,
        )

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                ),
            }
        )

    def load(self, source: Path) -> str:
        if not source.exists():
            raise FileNotFoundError(f"Document not found: {source}")

        if source.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {source.suffix}"
            )

        result = self.converter.convert(source)

        return result.document.export_to_markdown()

    def load_pages(self, source: Path) -> list[tuple[int, str]]:
        """Extract document elements grouped by their original PDF page."""
        if not source.exists():
            raise FileNotFoundError(f"Document not found: {source}")

        if source.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected a PDF file, got: {source.suffix}"
            )

        result = self.converter.convert(source)
        pages: dict[int, list[str]] = {}

        for element, _ in result.document.iterate_items():
            text = getattr(element, "text", None)

            if not text or not text.strip():
                continue

            provenance = getattr(element, "prov", None) or []

            if not provenance:
                continue

            page_number = provenance[0].page_no
            pages.setdefault(page_number, []).append(text.strip())

        return [
            (page_number, "\n\n".join(texts))
            for page_number, texts in sorted(pages.items())
        ]