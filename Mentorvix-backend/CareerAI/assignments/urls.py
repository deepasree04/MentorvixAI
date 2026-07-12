from django.urls import path
from .views import upload_assignment, list_assignments, analyze_assignment, get_assignment, assignment_page, upload_page, review_page

urlpatterns = [
    path('upload/', upload_assignment),
    path('upload-page/', upload_page, name='upload_page'),
    path('list/', list_assignments),
    path('analyze/<int:pk>/', analyze_assignment),
    path('review/', review_page, name='review_page'),
    path('<int:pk>/', get_assignment),
    path('', assignment_page, name='assignment_page')
]