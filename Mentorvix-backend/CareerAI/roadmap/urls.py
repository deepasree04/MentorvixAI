from django.urls import path
from .views import roadmap_api

urlpatterns = [
    path("", roadmap_api,),
]