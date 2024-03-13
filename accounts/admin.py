from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Client


@admin.register(Client)
class ClientAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone",
        "date_of_birth",
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
        "date_of_birth",
    )
    ordering = ("username",)
