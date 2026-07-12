"""Document loaders for PDF, DOCX, and TXT files."""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document

from .embeddings import InvalidDocumentError, UnsupportedFileTypeError

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".docx", ".txt", ".md", ".markdown"})


def get_file_type(file_path: Path) -> str:
    """Return the normalized file extension for *file_path*."""
    extension = file_path.suffix.lower()
    if extension == ".markdown":
        return ".md"
    return extension


def validate_file_path(file_path: str | Path) -> Path:
    """Resolve and validate that *file_path* exists and is a supported type."""
    path = Path(file_path).resolve()

    if not path.is_file():
        raise InvalidDocumentError(f"File not found: {path}")

    file_type = get_file_type(path)
    if file_type not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{path.suffix}'. Supported: {supported}"
        )

    return path


def _load_pdf(file_path: Path) -> list[Document]:
    loader = PyPDFLoader(str(file_path))
    return loader.load()


def _load_docx(file_path: Path) -> list[Document]:
    loader = Docx2txtLoader(str(file_path))
    return loader.load()


def _load_text(file_path: Path) -> list[Document]:
    loader = TextLoader(str(file_path), encoding="utf-8", autodetect_encoding=True)
    return loader.load()


def load_document(file_path: str | Path) -> list[Document]:
    """
    Load a single document and return LangChain ``Document`` objects.

    Supported formats: PDF, DOCX, TXT, Markdown (``.md`` / ``.markdown``).

    Each returned document is enriched with ``source``, ``file_type``, and
    ``filename`` metadata fields.
    """
    path = validate_file_path(file_path)
    file_type = get_file_type(path)

    try:
        if file_type == ".pdf":
            documents = _load_pdf(path)
        elif file_type == ".docx":
            documents = _load_docx(path)
        elif file_type in {".txt", ".md"}:
            documents = _load_text(path)
        else:
            raise UnsupportedFileTypeError(f"Unsupported file type: {file_type}")
    except (UnsupportedFileTypeError, InvalidDocumentError):
        raise
    except Exception as exc:
        logger.exception("Failed to load document: %s", path)
        raise InvalidDocumentError(f"Could not read file '{path.name}': {exc}") from exc

    if not documents:
        raise InvalidDocumentError(f"No content extracted from '{path.name}'.")

    source = str(path)
    filename = path.name

    for document in documents:
        document.metadata.setdefault("source", source)
        document.metadata["file_type"] = file_type
        document.metadata["filename"] = filename

    logger.info("Loaded %d page(s) from %s", len(documents), filename)
    return documents
