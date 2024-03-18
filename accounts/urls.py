# accounts/urls.py
from django.contrib.auth import urls as auth_urls
from django.urls import include, path

from .views import *

urlpatterns = [
    # standard auth urls
    path("login/", login, name="login"),
    path("log_out/", log_out, name="log_out"),
    path("signup/", register, name="signup"),
    path("contact/", contact, name="contact"),
    path("", include(auth_urls)),
]
