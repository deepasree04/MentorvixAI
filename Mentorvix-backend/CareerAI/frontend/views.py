from django.shortcuts import render


def home(request):
    return render(request, 'home_page/home.html')


def profile(request):
    return render(request, 'profile/profile.html')


def assignments(request):
    return render(request, 'assignment-page/listpage.html')


def chat(request):
    return render(request, 'chat/aichat.html')


def review(request):
    return render(request, 'chat/aireview.html')


def roadmap(request):
    return render(request, 'roadmap/roadmap.html')


def login_signup(request):
    return render(request, 'auth/loginsignup.html')
