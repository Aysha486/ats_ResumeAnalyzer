from django.shortcuts import render

from django.urls import path
from . import views

from django.contrib.auth.views import LogoutView



def register(request):
    return render(request, "register.html")

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", LogoutView.as_view(next_page="/authentication/login/"), name="logout"),
]