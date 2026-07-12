"""ChromaDB vector store access and similarity search."""

from __future__ import annotations

import logging
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document

from .embeddings import (
    RAG_COLLECTION_NAME,
    RAG_TOP_K,
    DocumentInfo,
    ensure_chroma_directory,
    get_embedding_model,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
    """Return a cached, persistent Chroma vector store."""
    persist_dir = ensure_chroma_directory()
    embeddings = get_embedding_model()

    return Chroma(
        collection_name=RAG_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(persist_dir),
    )


def add_documents(chunks: list[Document]) -> list[str]:
    """Embed and persist document chunks. Returns assigned chunk IDs."""
    if not chunks:
        return []

    vectorstore = get_vectorstore()
    ids = vectorstore.add_documents(chunks)
    logger.info("Indexed %d chunk(s) into Chroma collection '%s'.", len(ids), RAG_COLLECTION_NAME)
    return ids


def similarity_search(
    query: str,
    *,
    top_k: int | None = None,
) -> list[Document]:
    """Retrieve the most relevant document chunks for *query*."""
    k = top_k or RAG_TOP_K
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search(query, k=k)


def similarity_search_with_scores(
    query: str,
    *,
    top_k: int | None = None,
) -> list[tuple[Document, float]]:
    """Retrieve the most relevant document chunks along with their L2 distance scores."""
    k = top_k or RAG_TOP_K
    vectorstore = get_vectorstore()
    try:
        logger.info("Performing similarity search with scores for query: '%s'", query)
        return vectorstore.similarity_search_with_score(query, k=k)
    except Exception as exc:
        logger.exception("ChromaDB similarity search failed")
        raise


def delete_by_document_id(document_id: str, *, exclude_physical_path: str | Path | None = None) -> int:
    """
    Remove all chunks belonging to *document_id* and delete its physical file (unless excluded).

    Returns the number of chunks deleted.
    """
    collection = get_vectorstore()._collection  # noqa: SLF001 — Chroma internal API
    existing = collection.get(where={"document_id": document_id}, include=["metadatas"])

    # Attempt to physically delete the uploaded file
    metadatas = existing.get("metadatas") or []
    if metadatas and metadatas[0]:
        source_path = metadatas[0].get("source")
        if source_path:
            try:
                from pathlib import Path
                p = Path(source_path)
                
                should_delete = True
                if exclude_physical_path is not None:
                    p_exclude = Path(exclude_physical_path).resolve()
                    if p.resolve() == p_exclude:
                        should_delete = False
                        logger.info("Skipping physical deletion of %s as it is the target of a new index operation.", source_path)
                
                if should_delete and p.exists() and p.is_file():
                    p.unlink()
                    logger.info("Physically deleted document file: %s", source_path)
            except Exception as file_err:
                logger.warning("Could not delete physical file %s: %s", source_path, file_err)


    chunk_ids = existing.get("ids", [])
    if not chunk_ids:
        return 0

    collection.delete(ids=chunk_ids)
    logger.info("Deleted %d chunk(s) for document_id='%s' from ChromaDB.", len(chunk_ids), document_id)
    return len(chunk_ids)


def list_indexed_documents() -> list[DocumentInfo]:
    """Return a deduplicated list of indexed documents with comprehensive metadata."""
    collection = get_vectorstore()._collection  # noqa: SLF001
    result = collection.get(include=["metadatas"])

    metadatas = result.get("metadatas") or []
    counts: dict[str, dict[str, str | int]] = {}

    for metadata in metadatas:
        if not metadata:
            continue

        doc_id = metadata.get("document_id")
        if not doc_id:
            continue

        if doc_id not in counts:
            counts[doc_id] = {
                "document_id": doc_id,
                "source": metadata.get("source", ""),
                "file_type": metadata.get("file_type", ""),
                "chunk_count": 0,
                "filename": metadata.get("filename", ""),
                "upload_time": metadata.get("upload_time", ""),
                "file_size": metadata.get("file_size", 0),
                "status": metadata.get("status", "Indexed"),
            }

        counts[doc_id]["chunk_count"] = int(counts[doc_id]["chunk_count"]) + 1

    documents = [
        DocumentInfo(
            document_id=str(item["document_id"]),
            source=str(item["source"]),
            file_type=str(item["file_type"]),
            chunk_count=int(item["chunk_count"]),
            filename=str(item["filename"]),
            upload_time=str(item["upload_time"]),
            file_size=int(item["file_size"]),
            status=str(item["status"]),
        )
        for item in counts.values()
    ]
    return sorted(documents, key=lambda doc: doc.source.lower())



def document_exists(document_id: str) -> bool:
    """Return True if at least one chunk exists for *document_id*."""
    collection = get_vectorstore()._collection  # noqa: SLF001
    result = collection.get(where={"document_id": document_id}, include=[])
    return bool(result.get("ids"))
