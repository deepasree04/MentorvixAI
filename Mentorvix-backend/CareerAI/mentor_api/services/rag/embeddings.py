"""Embedding model factory and shared configurations/exceptions."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# ---------------------------------------------------------------------------
# Shared Configuration & Constants
# ---------------------------------------------------------------------------
RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "4"))
RAG_COLLECTION_NAME: str = os.getenv("RAG_COLLECTION_NAME", "mentorvix_knowledge")
RAG_EMBEDDING_MODEL: str = os.getenv("RAG_EMBEDDING_MODEL", "models/gemini-embedding-001")

_DEFAULT_CHROMA_DIR = Path(__file__).resolve().parent.parent.parent / "rag_data" / "chroma"
RAG_CHROMA_PERSIST_DIR: Path = Path(
    os.getenv("RAG_CHROMA_PERSIST_DIR", str(_DEFAULT_CHROMA_DIR))
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class RAGError(Exception):
    """Base exception for RAG operations."""


class UnsupportedFileTypeError(RAGError):
    """Raised when a file extension is not supported."""


class DocumentNotFoundError(RAGError):
    """Raised when a document ID does not exist in the vector store."""


class InvalidDocumentError(RAGError):
    """Raised when a file path is missing or unreadable."""


# ---------------------------------------------------------------------------
# Shared Data Classes
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DocumentInfo:
    """Summary of an indexed document."""

    document_id: str
    source: str
    file_type: str
    chunk_count: int
    filename: str = ""
    upload_time: str = ""
    file_size: int = 0
    status: str = "Indexed"



@dataclass(frozen=True)
class IndexResult:
    """Result of indexing a single document."""

    document_id: str
    source: str
    file_type: str
    chunks_indexed: int


# ---------------------------------------------------------------------------
# Helpers & Factories
# ---------------------------------------------------------------------------
def ensure_chroma_directory() -> Path:
    """Create the Chroma persist directory if it does not exist."""
    RAG_CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    return RAG_CHROMA_PERSIST_DIR


@lru_cache(maxsize=1)
def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """
    Return a cached Gemini embedding model instance.

    Uses the same ``GEMINI_API_KEY`` environment variable as the chat LLM,
    but operates independently so chat code remains untouched.
    """
    api_key = os.getenv("Gemini_API_KEY") or os.getenv("Gemini_API_KEY")
    if not api_key:
        raise RAGError(
            "GEMINI_API_KEY is not set. Add it to your environment or .env file."
        )

    return GoogleGenerativeAIEmbeddings(
        model=RAG_EMBEDDING_MODEL,
        google_api_key=api_key,
    )
