// Reusable API calls for MentorVix document management and upload pipeline

/**
 * Get cookie by name (used for CSRF token retrieval)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Fetch all indexed documents from ChromaDB.
 * GET /api/rag/documents/
 */
async function fetchDocuments() {
    const response = await fetch("/api/rag/documents/", {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    });
    if (!response.ok) {
        throw new Error("Failed to fetch documents from knowledge base.");
    }
    return await response.json();
}

/**
 * Upload a document to ChromaDB.
 * POST /api/rag/upload/
 * Supports custom progress handler using XMLHttpRequest.
 */
function uploadDocument(file, { onProgress, onSuccess, onError }) {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("file", file);

    xhr.open("POST", "/api/rag/upload/", true);
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));

    // Track upload progress
    if (xhr.upload && onProgress) {
        xhr.upload.addEventListener("progress", (event) => {
            if (event.lengthComputable) {
                const percentComplete = Math.round((event.loaded / event.total) * 100);
                onProgress(percentComplete);
            }
        });
    }

    xhr.onload = function() {
        let responseData = {};
        try {
            responseData = JSON.parse(xhr.responseText);
        } catch (e) {
            responseData = { error: "Invalid JSON response from server" };
        }

        if (xhr.status >= 200 && xhr.status < 300) {
            onSuccess(responseData);
        } else {
            onError(responseData.error || `Upload failed with status ${xhr.status}`);
        }
    };

    xhr.onerror = function() {
        onError("Network error. Please check your connection.");
    };

    xhr.send(formData);
    return xhr;
}

/**
 * Delete a document from ChromaDB.
 * DELETE /api/rag/documents/{document_id}/
 */
async function deleteDocument(documentId) {
    const response = await fetch(`/api/rag/documents/${documentId}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }
    });
    if (!response.ok) {
        const responseData = await response.json().catch(() => ({}));
        throw new Error(responseData.error || `Failed to delete document ${documentId}.`);
    }
    return await response.json();
}
