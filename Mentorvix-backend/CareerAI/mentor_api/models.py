from django.db import models
from django.contrib.auth.models import User

class Career(models.Model):
    name = models.CharField(max_length=100)
    interest = models.CharField(max_length=100)
    suggested_career = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Assignment(models.Model):
    file_name = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10) # 'user' or 'ai'
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    rag_used = models.BooleanField(default=False)
    sources = models.JSONField(null=True, blank=True) # stores citations metadata (filename, page, chunk, confidence)
    latency = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.role}: {self.message[:30]}"

# Create your models here.
