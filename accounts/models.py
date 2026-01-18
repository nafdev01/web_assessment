from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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
