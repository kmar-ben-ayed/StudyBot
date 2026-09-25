"""
DocumentLoader: turns a PDF file into clean plain text.

Kept deliberately simple: one class, one job. Uses PyMuPDF (fitz) because it
is fast, dependency-light, and returns good quality text for most PDFs.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pymupdf as fitz  # PyMuPDF (the `pymupdf` import name replaces the older `fitz` alias)


class DocumentLoadError(Exception):
    """Raised when a document cannot be loaded or contains no usable text."""


@dataclass
class LoadedDocument:
    path: Path
    num_pages: int
    text: str

    @property
    def num_characters(self) -> int:
        return len(self.text)


def _clean_text(raw_text: str) -> str:
    """Collapse excessive whitespace produced by PDF extraction."""
    text = raw_text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class DocumentLoader:
    """Loads a PDF file and extracts cleaned text from it."""

    def load(self, path: str | Path) -> LoadedDocument:
        pdf_path = Path(path)
        if not pdf_path.exists():
            raise DocumentLoadError(f"File not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise DocumentLoadError(f"Only PDF files are supported, got: {pdf_path.suffix}")

        try:
            doc = fitz.open(pdf_path)
        except Exception as exc:  # corrupt/unreadable file
            raise DocumentLoadError(f"Could not open PDF: {exc}") from exc

        try:
            pages_text = [page.get_text("text") for page in doc]
            num_pages = doc.page_count
        finally:
            doc.close()

        full_text = _clean_text("\n\n".join(pages_text))

        if not full_text:
            raise DocumentLoadError(
                "The PDF contains no extractable text (it may be a scanned "
                "image). Try a text-based PDF instead."
            )

        return LoadedDocument(path=pdf_path, num_pages=num_pages, text=full_text)
