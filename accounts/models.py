from django.db import models
from django.contrib.auth.models import AbstractUser


class Client(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
