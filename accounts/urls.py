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
    path("profile/", profile, name="profile"),
    path("verify-email/<uuid:token>/", verify_email, name="verify_email"),
    path("resend-verification/", resend_verification_email, name="resend_verification"),
    path("", include(auth_urls)),
]
