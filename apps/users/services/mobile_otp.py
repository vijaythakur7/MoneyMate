
import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.users.models import MobileOTP


OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 5


def _hash_otp(otp: str) -> str:
    """Hash the OTP using Django's secret key."""
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        otp.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def generate_mobile_otp(user) -> str:
    """Generate a six-digit OTP and store its hash."""
    otp = f"{secrets.randbelow(1_000_000):06d}"
    now = timezone.now()

    with transaction.atomic():
        # Invalidate all previously unused OTPs for this user.
        MobileOTP.objects.filter(
            user=user,
            is_used=False,
        ).update(is_used=True)

        MobileOTP.objects.create(
            user=user,
            otp_hash=_hash_otp(otp),
            expires_at=now + timedelta(
                minutes=OTP_EXPIRY_MINUTES
            ),
        )

    # Return the plain OTP only to the SMS delivery code.
    return otp


def verify_mobile_otp(user, otp: str) -> bool:
    """Validate an OTP and allow it to be used only once."""
    with transaction.atomic():
        record = (
            MobileOTP.objects.select_for_update()
            .filter(user=user, is_used=False)
            .order_by("-created_at", "-pk")
            .first()
        )

        if record is None:
            return False

        if record.expires_at <= timezone.now():
            record.is_used = True
            record.save(update_fields=["is_used"])
            return False

        if record.attempts >= MAX_OTP_ATTEMPTS:
            record.is_used = True
            record.save(update_fields=["is_used"])
            return False

        # Reject malformed input and count it as an attempt.
        if (
            not isinstance(otp, str)
            or len(otp) != 6
            or not otp.isascii()
            or not otp.isdigit()
        ):
            record.attempts += 1
            if record.attempts >= MAX_OTP_ATTEMPTS:
                record.is_used = True

            record.save(
                update_fields=["attempts", "is_used"]
            )
            return False

        submitted_hash = _hash_otp(otp)

        if not hmac.compare_digest(
            record.otp_hash,
            submitted_hash,
        ):
            record.attempts += 1

            if record.attempts >= MAX_OTP_ATTEMPTS:
                record.is_used = True

            record.save(
                update_fields=["attempts", "is_used"]
            )
            return False

        record.is_used = True
        record.save(update_fields=["is_used"])

        return True
