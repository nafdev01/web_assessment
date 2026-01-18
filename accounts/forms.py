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
            "password1",
            "password2",
        ]
        help_texts = {
            "username": None,
            "email": None,
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ("name", "email", "subject", "message")


class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})
