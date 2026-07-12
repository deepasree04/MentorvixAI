from django.urls import path
from . import views, upload_views

urlpatterns = [
    path("", views.home, name="home"),
    path('ai-chat/', views.ai_chat_page),
    path("api/ai-chat/", views.ai_chat, name="ai_chat_api"),
    path('knowledge-base/', views.knowledge_base_page, name='knowledge_base'),
    
    # Conversations API routes
    path("api/conversations/", views.list_conversations, name="list_conversations"),
    path("api/conversations/<int:conversation_id>/", views.conversation_detail, name="conversation_detail"),

    # RAG analytics dashboard API
    path("api/rag/stats/", views.rag_stats, name="rag_stats"),

    # RAG API routes
    path("api/rag/upload/", upload_views.rag_upload, name="rag_upload"),
    path("api/rag/documents/", upload_views.rag_list_documents, name="rag_list_documents"),
    path("api/rag/documents/<str:document_id>/", upload_views.rag_delete_document, name="rag_delete_document"),
]