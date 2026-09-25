import pytest

from app.rag.loader import DocumentLoader, DocumentLoadError


def test_load_sample_pdf_extracts_text(sample_pdf_path):
    loader = DocumentLoader()
    document = loader.load(sample_pdf_path)

    assert document.num_pages >= 1
    assert document.num_characters > 0
    assert "operating system" in document.text.lower()


def test_missing_file_raises():
    loader = DocumentLoader()
    with pytest.raises(DocumentLoadError):
        loader.load("data/does_not_exist.pdf")


def test_non_pdf_extension_raises(tmp_path):
    loader = DocumentLoader()
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("hello")
    with pytest.raises(DocumentLoadError):
        loader.load(txt_file)
