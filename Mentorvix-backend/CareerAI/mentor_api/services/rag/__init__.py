"""
MentorVix RAG package — document indexing and retrieval backend.
"""

from .embeddings import (
    DocumentInfo,
    DocumentNotFoundError,
    IndexResult,
    InvalidDocumentError,
    RAGError,
    UnsupportedFileTypeError,
)
from .services import (
    delete_document,
    index_documents,
    list_documents,
    retrieve_context,
    retrieve_detailed_context,
)

__all__ = [
    "DocumentInfo",
    "DocumentNotFoundError",
    "IndexResult",
    "InvalidDocumentError",
    "RAGError",
    "UnsupportedFileTypeError",
    "delete_document",
    "index_documents",
    "list_documents",
    "retrieve_context",
    "retrieve_detailed_context",
]
