# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Client, Contact


class ClientRegistrationForm(UserCreationForm):
    class Meta:
        model = Client
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "address",
            "password1",
            "password2",
        ]
        help_texts = {
            "username": None,
            "email": None,
        }
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ("name", "email", "subject", "message")
