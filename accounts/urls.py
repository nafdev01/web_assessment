# accounts/urls.py
from django.urls import path, include
from .views import *
from django.contrib.auth import urls as auth_urls


urlpatterns = [
    # standard auth urls
    path("login/", login, name="login"),
    path("log_out/", log_out, name="log_out"),
    path("signup/", register, name="signup"),
    path("", include(auth_urls)),
]
