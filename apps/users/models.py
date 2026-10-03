from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)

    mobile_number = models.CharField(
        max_length=15,
        blank=True,
    )

    currency = models.CharField(
        max_length=3,
        default="INR",
    )

    timezone = models.CharField(
        max_length=50,
        default="Asia/Kolkata",
    )

    is_email_verified = models.BooleanField(
        default=False,
    )