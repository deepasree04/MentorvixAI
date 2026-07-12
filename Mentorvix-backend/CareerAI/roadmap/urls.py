from django.urls import path
from .views import roadmap_page, roadmap_api

urlpatterns = [
    path('', roadmap_page, name='roadmap_page'),
    path("api/", roadmap_api, name="roadmap_api"),
]