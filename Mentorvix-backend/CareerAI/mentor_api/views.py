import logging
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import google.generativeai as genai
import os
from dotenv import load_dotenv
from .services.rag import retrieve_context, retrieve_detailed_context
import time

load_dotenv()

logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("Gemini_API_KEY"))
# --- Configuration ---

# Initialize the Gemini 2.0 Flash model with system instructions
# This defines the persona of MENTORVIX AI
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=(
        "You are MENTORVIX AI, a helpful career assistant. "
        "You give concise, practical advice on career paths, skills, roadmaps, "
        "and learning resources. Keep responses friendly and to the point."
    )
)

# --- Page Views ---

@api_view(['GET'])
def home(request):
    """Renders the main landing page."""
    return render(request, "home_page/home.html")




def ai_chat_page(request):
    """Renders the dedicated AI chat interface."""
    return render(request, "chat/aichat.html")


def knowledge_base_page(request):
    """Renders the knowledge base management interface."""
    return render(request, "upload/knowledge_base.html")


# --- API Logic ---

from django.db import models as django_models
from .models import Conversation, ChatMessage

@api_view(["GET"])
def list_conversations(request):
    """Lists all conversations, filtered by user if logged in."""
    try:
        user = request.user if request.user.is_authenticated else None
        conversations = Conversation.objects.filter(user=user).order_by("-updated_at")
        
        data = []
        for conv in conversations:
            data.append({
                "conversation_id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            })
        return Response(data, status=200)
    except Exception as e:
        logger.exception("Error listing conversations")
        return Response({"error": str(e)}, status=500)


@api_view(["GET", "DELETE"])
def conversation_detail(request, conversation_id):
    """Fetch history of a conversation or delete it."""
    try:
        user = request.user if request.user.is_authenticated else None
        conv = Conversation.objects.get(id=conversation_id, user=user)
    except Conversation.DoesNotExist:
        return Response({"error": "Conversation not found"}, status=404)

    if request.method == "GET":
        try:
            messages = conv.messages.all().order_by("timestamp")
            msg_list = []
            for msg in messages:
                msg_list.append({
                    "id": msg.id,
                    "role": msg.role,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat(),
                    "rag_used": msg.rag_used,
                    "sources": msg.sources
                })
            return Response({
                "conversation_id": conv.id,
                "title": conv.title,
                "messages": msg_list
            }, status=200)
        except Exception as e:
            logger.exception("Error fetching conversation detail")
            return Response({"error": str(e)}, status=500)

    elif request.method == "DELETE":
        try:
            conv.delete()
            return Response({"message": "Conversation deleted successfully"}, status=200)
        except Exception as e:
            logger.exception("Error deleting conversation")
            return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def rag_stats(request):
    """
    Returns analytics stats: total uploaded documents, total chunks, total conversations,
    total AI requests, RAG usage percentage, average response time.
    """
    try:
        # Retrieve documents from ChromaDB
        from .services.rag import list_documents
        documents = list_documents()
        total_docs = len(documents)
        total_chunks = sum(doc.chunk_count for doc in documents)

        # Retrieve DB stats
        total_conversations = Conversation.objects.count()
        
        ai_messages = ChatMessage.objects.filter(role="ai")
        total_ai_requests = ai_messages.count()
        
        if total_ai_requests > 0:
            rag_count = ai_messages.filter(rag_used=True).count()
            rag_percentage = round((rag_count / total_ai_requests) * 100, 1)
            avg_time = round(ai_messages.aggregate(django_models.Avg("latency"))["latency__avg"] or 0.0, 3)
        else:
            rag_percentage = 0.0
            avg_time = 0.0

        return Response({
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "total_conversations": total_conversations,
            "total_ai_requests": total_ai_requests,
            "rag_percentage": rag_percentage,
            "average_response_time": avg_time
        })
    except Exception as e:
        logger.exception("Error calculating RAG stats")
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def ai_chat(request):
    """
    Handles POST requests from the frontend, retrieves relevant RAG context,
    sends user input along with context and memory history to Gemini, and stores chat logs.
    """
    user_input = request.data.get("message")
    conversation_id = request.data.get("conversation_id")

    if not user_input:
        return Response({"error": "No input provided"}, status=400)

    try:
        user = request.user if request.user.is_authenticated else None
        
        # 1. Fetch or create Conversation thread
        if conversation_id:
            try:
                conv = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                return Response({"error": "Conversation not found"}, status=404)
        else:
            # Generate title from first 5 words of user input
            words = user_input.split()[:5]
            title = " ".join(words) if words else "New Conversation"
            conv = Conversation.objects.create(user=user, title=title)
            conversation_id = conv.id

        # 2. Save user message to database
        ChatMessage.objects.create(
            conversation=conv,
            role="user",
            message=user_input
        )

        # 3. Retrieve conversation history memory (limit to last 6 messages to prevent token limits)
        history_messages = ChatMessage.objects.filter(conversation=conv).order_by("-timestamp")[:6]
        # Reverse to chronological order
        history_messages = list(reversed(history_messages))
        
        history_str = ""
        for msg in history_messages:
            if msg.message != user_input or msg.role != "user":  # avoid duplicating current input
                history_str += f"{'User' if msg.role == 'user' else 'AI'}: {msg.message}\n"

        # 4. Retrieve detailed context and sources from vector store
        context, sources = retrieve_detailed_context(user_input)
        rag_used = bool(context)

        # 5. Formulate grounded prompt containing memory history and reference context
        if context:
            prompt = (
                "You are MENTORVIX AI, a helpful career assistant. "
                "Use the following reference material to answer the user's question. "
                "If the reference material does not contain the answer, use your own knowledge. "
                "Keep your answer concise and helpful.\n\n"
                f"--- Reference Material ---\n{context}\n"
                f"--- End Reference Material ---\n\n"
                f"Conversation History:\n{history_str}"
                f"User: {user_input}\n"
                "AI:"
            )
        else:
            prompt = (
                "You are MENTORVIX AI, a helpful career assistant. "
                "Give concise, practical advice on career paths, skills, roadmaps, and learning resources.\n\n"
                f"Conversation History:\n{history_str}"
                f"User: {user_input}\n"
                "AI:"
            )

        # 6. Execute Gemini request, measuring latency
        start_time = time.time()
        try:
            response = model.generate_content(prompt)
        except Exception as gemini_err:
            logger.exception("Gemini API call failed")
            return Response(
                { "error": str(gemini_err),
            "type": type(gemini_err).__name__},
                status=503
            )

        response_latency = time.time() - start_time
        logger.info("Gemini API response time: %.3f seconds", response_latency)

        reply = response.text
        
        # 7. Append citation blocks to reply text for display fallback
        if rag_used:
            citation = "\n\n---\n*Generated using uploaded knowledge.*\n**Sources used:**"
            for src in sources:
                page_info = f", Page: {src['page']}" if src['page'] is not None else ""
                citation += f"\n- {src['filename']} (Chunk: {src['chunk']}{page_info}, Confidence: {src['confidence']}% )"
            reply += citation

        # 8. Save AI response to database (raw content only, preserving clean history)
        ChatMessage.objects.create(
            conversation=conv,
            role="ai",
            message=response.text,
            rag_used=rag_used,
            sources=sources,
            latency=response_latency
        )
        
        # Update conversation timestamp
        conv.save()

        # 9. Return structured response
        return Response({
            "conversation_id": conversation_id,
            "reply": reply,
            "rag_used": rag_used,
            "sources": sources
        })

    except Exception as e:
        logger.exception("Exception occurred in ai_chat view: %s", str(e))
        return Response({"error": str(e)}, status=500)