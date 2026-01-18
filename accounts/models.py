from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta


class Client(AbstractUser):
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=50)
    message = models.TextField()
    contact_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.email} - {self.contact_at}"

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"


class EmailVerification(models.Model):
    user = models.OneToOneField(Client, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    verified = models.BooleanField(default=False)
    token_created_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Verified: {self.verified}"

    def is_expired(self):
        return timezone.now() > self.token_created_at + timedelta(minutes=10)

    def regenerate_token(self):
        self.token = uuid.uuid4()
        self.token_created_at = timezone.now()
        self.save()
