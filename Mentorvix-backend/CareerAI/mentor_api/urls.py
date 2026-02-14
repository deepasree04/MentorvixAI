from django.urls import path
from . import views
from .views import ai_chat
urlpatterns = [
    path("", views.home, name="home"),
    path('ai-chat/', ai_chat),

]
