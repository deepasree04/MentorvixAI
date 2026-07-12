# 🚀 MentorVix AI – Intelligent Career Guidance Platform

> An AI-powered career guidance platform that combines **Large Language Models (LLMs)** with **Retrieval-Augmented Generation (RAG)** to deliver personalized, context-aware career assistance.


---

## 📌 Overview

MentorVix AI is a full-stack AI application designed to provide personalized career guidance, learning roadmaps, resume-based assistance, and intelligent document-aware conversations.

Unlike traditional AI chatbots, MentorVix integrates **Retrieval-Augmented Generation (RAG)**, enabling users to upload documents such as resumes, study materials, or company PDFs. The AI retrieves relevant information from those documents before generating responses, resulting in more accurate and context-aware answers.

The project demonstrates modern AI application development using **Django**, **LangChain**, **Google Gemini**, and **ChromaDB**.

---
## 🌐 Live Demo 
https://mentorvixai.onrender.com
---

# ✨ Key Features

## 🤖 AI Career Assistant

- Career guidance powered by Google Gemini
- Learning roadmap recommendations
- Skill improvement suggestions
- Personalized career advice

---

## 📚 Retrieval-Augmented Generation (RAG)

- Upload PDF & DOCX documents
- Automatic document chunking
- Semantic embeddings generation
- Vector search using ChromaDB
- Context-aware AI responses
- Automatic fallback to standard Gemini chat when no relevant documents exist

---

## 📂 Knowledge Base

- Upload documents
- View indexed documents
- Delete documents
- Chunk statistics
- File type information

---

## 💬 AI Chat

- Intelligent conversation memory
- Context-aware responses
- Source-aware retrieval
- Chat history support

---

## 📈 Analytics Dashboard

- Uploaded documents count
- Indexed chunk count
- AI request statistics
- RAG usage percentage
- Response time metrics

---

# 🏗️ System Architecture

```
                        User

                          │

                          ▼

                 MentorVix Frontend

                          │

                    REST API Request

                          ▼

              Django REST Framework API

                          │

          ┌───────────────┴───────────────┐
          │                               │

          ▼                               ▼

     ChromaDB Retrieval            Conversation History

          │                               │

          └───────────────┬───────────────┘

                          ▼

                 Prompt Construction

                          ▼

               Google Gemini 2.5 Flash

                          ▼

                   AI Generated Response
```

---

# 🛠️ Tech Stack

### Backend

- Python
- Django
- Django REST Framework
- JWT Authentication

### Artificial Intelligence

- Google Gemini 2.5 Flash
- LangChain
- Retrieval-Augmented Generation (RAG)

### Vector Database

- ChromaDB

### Frontend

- HTML
- CSS
- JavaScript

### Database

- SQLite (Development)

### Tools

- Git
- GitHub
- Postman

---

# 📂 Project Structure

```
MentorVix

├── Mentorvix-backend
│
├── mentor_api
│     ├── services
│     │      └── rag
│     ├── views.py
│     ├── upload_views.py
│     └── models.py
│
├── Mentorvix-frontend
│
├── knowledge_base
│
└── README.md
```

---

# 🚀 AI Workflow

### Document Upload

```
PDF / DOCX

      ↓

Document Loader

      ↓

Chunking

      ↓

Gemini Embeddings

      ↓

ChromaDB
```

---

### User Chat

```
User Question

      ↓

Retrieve Relevant Chunks

      ↓

Prompt Construction

      ↓

Gemini 2.5 Flash

      ↓

Grounded AI Response
```

---

# 🎯 Real-World Use Cases

- Career Guidance
- Resume Assistance
- Learning Roadmaps
- Interview Preparation
- Document-based AI Assistant
- Knowledge Management

---

# 📸 Screenshots


- Home Page
- AI Chat
- Knowledge Base
- Analytics Dashboard
- RAG Response

---

# ⚙️ Installation

```bash
git clone https://github.com/yourusername/MentorVix.git

cd MentorVix
```

Create a virtual environment

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Configure environment variables

```
GEMINI_API_KEY=YOUR_API_KEY
```

Run

```bash
python manage.py migrate

python manage.py runserver
```

---

# 📊 Project Highlights

✔ Full Stack AI Application

✔ Retrieval-Augmented Generation (RAG)

✔ LangChain Integration

✔ ChromaDB Vector Search

✔ Google Gemini Integration

✔ Semantic Search

✔ Context-Aware AI

✔ Document Management

✔ Knowledge Base

✔ REST APIs

---

# 🚧 Future Improvements

- PostgreSQL Support
- Docker
- CI/CD
- Cloud Deployment
- Multi-user Knowledge Base
- Streaming AI Responses
- Multi-Agent AI
- Role-Based Access Control

---

# 👩‍💻 Developer

**Deepasree Somasundharam**

- LinkedIn:https://www.linkedin.com/in/deepasree-somasundharam/
- GitHub: https://github.com/deepasree04


---

# ⭐ If you found this project useful

Please consider giving it a ⭐ on GitHub.
