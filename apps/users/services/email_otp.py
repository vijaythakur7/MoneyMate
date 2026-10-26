import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.users.models import EmailOTP


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