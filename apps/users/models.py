import hashlib
import hmac

from django.conf import settings

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


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



from django.db import models
from django.utils import timezone as django_timezone


class EmailOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_otps",
    )

    otp_hash = models.CharField(max_length=64)

    expires_at = models.DateTimeField()

    attempts = models.PositiveSmallIntegerField(default=0)

    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return django_timezone.now() >= self.expires_at

    def verify_otp(self, otp):
        submitted_hash = hmac.new(
        settings.SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256,
    ).hexdigest()

        return hmac.compare_digest(
        submitted_hash,
        self.otp_hash,
    )

    def __str__(self):
        return f"Email OTP for user {self.user_id}"





class PendingRegistration(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    password_hash = models.CharField(max_length=128)

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

    otp_hash = models.CharField(max_length=64)
    otp_expires_at = models.DateTimeField()

    otp_created_at = models.DateTimeField(
        default=django_timezone.now,
    )

    otp_attempts = models.PositiveSmallIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]

    def is_otp_expired(self):
        return django_timezone.now() >= self.otp_expires_at

    def verify_otp(self, otp):
        submitted_hash = hmac.new(
            settings.SECRET_KEY.encode(),
            otp.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            submitted_hash,
            self.otp_hash,
        )

    def __str__(self):
        return f"Pending registration: {self.email}"
