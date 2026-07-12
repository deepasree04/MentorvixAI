from django.urls import path
from .views import register, login_page, login,  profile_page, profile

urlpatterns = [
    path('register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('login/', login_page, name='login_page'),
    path('profile/', profile_page, name='profile_page'),
    path('api/profile/', profile, name='profile_api')

]