from django.contrib.auth.models import AbstractUser
from django.db import models


class Client(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
