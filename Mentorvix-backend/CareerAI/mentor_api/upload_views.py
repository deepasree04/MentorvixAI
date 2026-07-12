import os
import logging
import hashlib
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.rag import index_documents, list_documents, delete_document
from .services.rag import DocumentNotFoundError, RAGError
from .services.rag.retriever import get_vectorstore
from .upload_serializers import (
    DocumentInfoSerializer,
    IndexResultSerializer,
    RAGUploadSerializer,
)

logger = logging.getLogger(__name__)


@api_view(["POST"])
def rag_upload(request):
    """
    Upload a document (PDF, DOCX, TXT, MD), save it locally, and index it into ChromaDB.
    """
    serializer = RAGUploadSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Upload validation failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = serializer.validated_data["file"]
    logger.info("Received upload request for file: %s (%d bytes)", uploaded_file.name, uploaded_file.size)

    try:
        # Calculate file content hash to detect duplicates prior to disk write
        hasher = hashlib.sha256()
        for chunk in uploaded_file.chunks():
            hasher.update(chunk)
        file_hash = hasher.hexdigest()

        # Query ChromaDB collection directly by content hash
        collection = get_vectorstore()._collection
        existing_by_hash = collection.get(where={"file_hash": file_hash}, limit=1)
        if existing_by_hash and existing_by_hash.get("ids"):
            logger.warning("Upload rejected: Duplicate document content detected for %s", uploaded_file.name)
            return Response({"error": "Document already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle filename collisions (Delete old database reference & file before writing new one)
        existing_by_name = collection.get(where={"filename": uploaded_file.name}, limit=1)
        if existing_by_name and existing_by_name.get("ids"):
            metadatas = existing_by_name.get("metadatas", [])
            if metadatas and metadatas[0]:
                old_doc_id = metadatas[0].get("document_id")
                if old_doc_id:
                    logger.info("Replacing collision file on disk and ChromaDB: %s (id: %s)", uploaded_file.name, old_doc_id)
                    delete_document(old_doc_id)

    except Exception as check_err:
        logger.exception("Failed to run preliminary duplicate checks: %s", check_err)
        return Response({"error": f"Failed duplicate checks: {check_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Save the file to media/rag_uploads/
    upload_dir = os.path.join(settings.MEDIA_ROOT, "rag_uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    fs = FileSystemStorage(location=upload_dir)
    filename = fs.save(uploaded_file.name, uploaded_file)
    file_path = os.path.join(upload_dir, filename)

    try:
        logger.info("Indexing saved document file on disk: %s", file_path)
        # Run indexing pipeline (loads, chunks, embeds, and indexes document)
        results = index_documents(file_path)
        if not results:
            logger.error("Indexing completed but returned empty results for: %s", filename)
            return Response({"error": "Failed to index the document"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Return the indexing summary
        response_serializer = IndexResultSerializer(results[0])
        logger.info("Successfully uploaded and indexed document: %s", filename)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except RAGError as e:
        logger.warning("RAG indexing error during upload of %s: %s", filename, e)
        # Cleanup the file on failure
        if os.path.exists(file_path):
            os.remove(file_path)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception("Unexpected exception during ingestion of %s", filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        return Response({"error": f"Internal server error during indexing: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def rag_list_documents(request):
    """
    List all indexed documents with their metadata and chunk counts.
    """
    logger.info("Received request to list indexed documents.")
    try:
        documents = list_documents()
        logger.info("Successfully fetched %d indexed document(s).", len(documents))
        serializer = DocumentInfoSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception("Error listing indexed documents")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
def rag_delete_document(request, document_id):
    """
    Delete all chunks of a document from ChromaDB.
    """
    logger.info("Received delete request for document_id: %s", document_id)
    try:
        deleted_count = delete_document(document_id)
        logger.info("Successfully deleted document_id: %s (%d chunks deleted)", document_id, deleted_count)
        return Response({
            "message": f"Successfully deleted document '{document_id}'",
            "chunks_deleted": deleted_count
        }, status=status.HTTP_200_OK)
      
    except DocumentNotFoundError as e:
        logger.warning("Delete target document_id %s not found: %s", document_id, e)
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
      
    except Exception as e:
        logger.exception("Unexpected error deleting document_id %s", document_id)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
