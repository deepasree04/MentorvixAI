"""High-level RAG service functions for indexing and retrieval."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .loader import load_document, validate_file_path
from .retriever import (
    add_documents,
    delete_by_document_id,
    document_exists,
    list_indexed_documents,
    similarity_search,
)
from .embeddings import (
    DocumentInfo,
    DocumentNotFoundError,
    IndexResult,
    RAG_CHUNK_SIZE,
    RAG_CHUNK_OVERLAP,
    RAGError,
)

logger = logging.getLogger(__name__)


def get_file_hash(path: Path) -> str:
    """Calculate the SHA-256 hash of a file's content to detect duplicates."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_document_id(file_path: Path) -> str:
    """Derive a stable document ID from the absolute file path."""
    digest = hashlib.sha256(str(file_path).encode("utf-8")).hexdigest()
    return digest[:16]


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Return a configured text splitter for document chunking."""
    return RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )


def _attach_chunk_metadata(
    chunks: list[Document],
    *,
    document_id: str,
    source: str,
    file_type: str,
    filename: str,
    upload_time: str,
    file_size: int,
    file_hash: str,
) -> list[Document]:
    """Enrich each chunk with indexing metadata used for management operations."""
    enriched: list[Document] = []

    for index, chunk in enumerate(chunks):
        metadata = {
            **chunk.metadata,
            "document_id": document_id,
            "source": source,
            "file_type": file_type,
            "filename": filename,
            "upload_time": upload_time,
            "file_size": file_size,
            "file_hash": file_hash,
            "status": "Indexed",
            "chunk_index": index,
        }
        enriched.append(Document(page_content=chunk.page_content, metadata=metadata))

    return enriched


def index_documents(
    file_paths: str | Path | list[str | Path],
    *,
    document_ids: list[str] | None = None,
    replace_existing: bool = True,
) -> list[IndexResult]:
    """
    Load, chunk, embed, and store one or more documents in ChromaDB with duplicate protection.
    """
    if isinstance(file_paths, (str, Path)):
        paths: list[Path] = [validate_file_path(file_paths)]
    else:
        paths = [validate_file_path(path) for path in file_paths]

    if document_ids is not None and len(document_ids) != len(paths):
        raise ValueError("document_ids must match the number of file paths.")

    results: list[IndexResult] = []
    splitter = get_text_splitter()

    for index, path in enumerate(paths):
        filename = path.name
        file_hash = get_file_hash(path)
        file_size = path.stat().st_size
        upload_time = datetime.now(timezone.utc).isoformat()

        logger.info("Initializing index process for: %s (size: %d bytes)", filename, file_size)

        # 1. Content-based duplicate verification
        from .retriever import get_vectorstore
        collection = get_vectorstore()._collection
        existing_by_hash = collection.get(where={"file_hash": file_hash}, limit=1)
        if existing_by_hash and existing_by_hash.get("ids"):
            logger.warning("Duplicate content upload rejected: %s (hash: %s)", filename, file_hash)
            raise RAGError("Document already exists.")

        # 2. Filename-based collision verification (Overwrite/Replace old document)
        existing_by_name = collection.get(where={"filename": filename}, limit=1)
        if existing_by_name and existing_by_name.get("ids"):
            metadatas = existing_by_name.get("metadatas", [])
            if metadatas and metadatas[0]:
                old_doc_id = metadatas[0].get("document_id")
                if old_doc_id:
                    logger.info("Replacing existing document by name: %s (id: %s)", filename, old_doc_id)
                    delete_by_document_id(old_doc_id, exclude_physical_path=path)


        doc_id = (
            document_ids[index]
            if document_ids is not None
            else generate_document_id(path)
        )
        file_type = path.suffix.lower()
        if file_type == ".markdown":
            file_type = ".md"

        if replace_existing and document_exists(doc_id):
            delete_by_document_id(doc_id)

        try:
            raw_documents = load_document(path)
            chunks = splitter.split_documents(raw_documents)
            chunks = _attach_chunk_metadata(
                chunks,
                document_id=doc_id,
                source=str(path),
                file_type=file_type,
                filename=filename,
                upload_time=upload_time,
                file_size=file_size,
                file_hash=file_hash,
            )

            add_documents(chunks)
        except RAGError:
            raise
        except Exception as exc:
            logger.exception("Ingestion failed for file: %s", filename)
            raise RAGError(f"Ingestion failed for '{filename}': {exc}") from exc

        result = IndexResult(
            document_id=doc_id,
            source=str(path),
            file_type=file_type,
            chunks_indexed=len(chunks),
        )
        results.append(result)
        logger.info(
            "Successfully indexed '%s' as document_id='%s' (%d chunks).",
            path.name,
            doc_id,
            len(chunks),
        )

    return results


def retrieve_context(
    query: str,
    *,
    top_k: int | None = None,
    separator: str = "\n\n---\n\n",
) -> str:
    """
    Retrieve the most relevant chunks for *query* and return a single context string.
    """
    query = query.strip()
    if not query:
        return ""

    try:
        logger.info("Retrieving context for query: '%s'", query)
        chunks = similarity_search(query, top_k=top_k)
        if not chunks:
            logger.info("No relevant context found.")
            return ""

        formatted_sections: list[str] = []
        for chunk in chunks:
            source = chunk.metadata.get("source", "unknown")
            section = f"[Source: {source}]\n{chunk.page_content.strip()}"
            formatted_sections.append(section)

        return separator.join(formatted_sections)
    except Exception as exc:
        logger.exception("Error during retrieve_context")
        return ""


def retrieve_detailed_context(
    query: str,
    *,
    top_k: int | None = None,
) -> tuple[str, list[dict[str, any]]]:
    """
    Retrieve the most relevant chunks for *query* along with metadata about their sources.
    """
    query = query.strip()
    if not query:
        return "", []

    try:
        logger.info("Retrieving detailed context for query: '%s'", query)
        from .retriever import similarity_search_with_scores
        chunks_with_scores = similarity_search_with_scores(query, top_k=top_k)
        if not chunks_with_scores:
            logger.info("No relevant chunks retrieved.")
            return "", []

        logger.info("Retrieved %d relevant chunk(s).", len(chunks_with_scores))
        formatted_sections: list[str] = []
        sources: list[dict[str, any]] = []
        seen_sources = set()

        for chunk, distance in chunks_with_scores:
            source_path = chunk.metadata.get("source", "unknown")
            filename = chunk.metadata.get("filename", Path(source_path).name)
            
            # Map distance to confidence percentage: 1 / (1 + distance)
            confidence = round((1.0 / (1.0 + distance)) * 100, 1)
            
            # Apply similarity/distance threshold to ignore low similarity results (Smart Retrieval)
            if distance > 0.8:
                logger.info("Skipping low relevance chunk (distance: %.3f, confidence: %.1f%%)", distance, confidence)
                continue
            
            section = f"[Source: {source_path}]\n{chunk.page_content.strip()}"
            formatted_sections.append(section)
            
            page = chunk.metadata.get("page")
            chunk_num = chunk.metadata.get("chunk_index")
            
            source_key = (filename, confidence, page, chunk_num)
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                sources.append({
                    "filename": filename,
                    "confidence": confidence,
                    "page": page + 1 if page is not None else None,
                    "chunk": chunk_num if chunk_num is not None else 0
                })


        return "\n\n---\n\n".join(formatted_sections), sources
    except Exception as exc:
        logger.exception("Error during retrieve_detailed_context")
        # Graceful fallback: return empty context so the chat doesn't crash
        return "", []


def delete_document(document_id: str) -> int:
    """
    Delete all indexed chunks for *document_id*.

    Returns the number of deleted chunks. Raises ``DocumentNotFoundError`` when
    the ID does not exist.
    """
    deleted_count = delete_by_document_id(document_id)
    if deleted_count == 0:
        raise DocumentNotFoundError(f"No indexed document found for id '{document_id}'.")
    return deleted_count


def list_documents() -> list[DocumentInfo]:
    """List all indexed documents with chunk counts."""
    return list_indexed_documents()
