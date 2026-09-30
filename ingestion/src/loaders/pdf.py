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
            raise ValueError(f"Expected a PDF file, got: {source.suffix}")

        result = self.converter.convert(source)

        return result.document.export_to_markdown()