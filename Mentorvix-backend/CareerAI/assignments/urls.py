from django.urls import path
from .views import upload_assignment, list_assignments, analyze_assignment, get_assignment

urlpatterns = [
    path('upload/', upload_assignment),
    path('list/', list_assignments),
    path('analyze/<int:pk>/', analyze_assignment),
    path('<int:pk>/', get_assignment)
]