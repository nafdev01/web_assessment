from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Client, Contact


@admin.register(Client)
class ClientAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )
    ordering = ("username",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "message",
        "contact_at",
    )
    search_fields = (
        "name",
        "email",
        "message",
    )
    ordering = ("-contact_at",)
