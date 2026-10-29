
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

logger = logging.getLogger(__name__)


def _get_verify_service():
    """Return the configured Twilio Verify service."""
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    service_sid = settings.TWILIO_VERIFY_SERVICE_SID

    if not account_sid or not auth_token or not service_sid:
        raise ImproperlyConfigured(
            "Twilio Verify credentials and service SID must be configured."
        )

    client = Client(account_sid, auth_token)
    return client.verify.v2.services(service_sid)


def send_verification_code(mobile_number: str) -> str:
    """Ask Twilio Verify to send an SMS verification code."""
    mobile_number = mobile_number.strip()

    if (
        not mobile_number.startswith("+")
        or not mobile_number[1:].isdigit()
        or not 8 <= len(mobile_number[1:]) <= 15
    ):
        raise ValueError(
            "The mobile number must use E.164 format, "
            "for example +91XXXXXXXXXX."
        )

    service = _get_verify_service()

    try:
        verification = service.verifications.create(
            to=mobile_number,
            channel="sms",
        )
    except TwilioRestException:
        logger.exception("Twilio Verify could not start verification.")
        raise

    return verification.status


def check_verification_code(
    mobile_number: str,
    code: str,
) -> bool:
    """Ask Twilio Verify to validate the submitted code."""
    mobile_number = mobile_number.strip()

    if (
        not mobile_number.startswith("+")
        or not mobile_number[1:].isdigit()
        or not 8 <= len(mobile_number[1:]) <= 15
    ):
        raise ValueError("The mobile number must use E.164 format.")

    if (
        not isinstance(code, str)
        or len(code) != 6
        or not code.isascii()
        or not code.isdigit()
    ):
        return False

    service = _get_verify_service()

    try:
        check = service.verification_checks.create(
            to=mobile_number,
            code=code,
        )
    except TwilioRestException as exc:
        # An invalid or expired code must not verify the user.
        if exc.code in (20404, 60200, 60202, 60203, 60212):
            return False

        logger.exception("Twilio Verify could not check the code.")
        raise

    return check.status == "approved"
