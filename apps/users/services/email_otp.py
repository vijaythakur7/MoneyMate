import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.users.models import EmailOTP, PendingRegistration

OTP_EXPIRY_MINUTES = 5


def generate_email_otp(user):
    # Generate a cryptographically secure 6-digit OTP
    otp = f"{secrets.randbelow(1_000_000):06d}"

    # Hash the OTP using a server-side secret
    otp_hash = hmac.new(
        settings.SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256,
    ).hexdigest()

    # Invalidate previous unused OTPs for this user
    EmailOTP.objects.filter(
        user=user,
        is_used=False,
    ).update(is_used=True)

    # Store the new OTP hash and expiry time
    EmailOTP.objects.create(
        user=user,
        otp_hash=otp_hash,
        expires_at=timezone.now() + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        ),
    )

    return otp





def generate_pending_registration_otp(pending_registration):
    otp = f"{secrets.randbelow(1_000_000):06d}"

    otp_hash = hmac.new(
        settings.SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256,
    ).hexdigest()

    pending_registration.otp_hash = otp_hash
    pending_registration.otp_created_at = timezone.now()
    pending_registration.otp_expires_at = (
        timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    )
    pending_registration.otp_attempts = 0

    pending_registration.save(
        update_fields=[
            "otp_hash",
            "otp_created_at",
            "otp_expires_at",
            "otp_attempts",
        ]
    )

    return otp
