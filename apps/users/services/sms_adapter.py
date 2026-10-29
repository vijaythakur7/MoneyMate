
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

logger = logging.getLogger(__name__)


def _send_with_twilio(to: str, body: str) -> str:
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_FROM_NUMBER

    if not account_sid or not auth_token or not from_number:
        raise ImproperlyConfigured(
            "Twilio credentials and sender must be configured."
        )

    try:
        message = Client(account_sid, auth_token).messages.create(
            body=body,
            from_=from_number,
            to=to,
        )
    except TwilioRestException:
        logger.exception("Twilio SMS submission failed.")
        raise

    logger.info("SMS submitted to Twilio; SID=%s", message.sid)
    return message.sid


def send_sms(to: str, body: str) -> str:
    """Send SMS using the configured provider or a safe local test mode."""
    mode = settings.SMS_DELIVERY_MODE

    if not to.startswith("+") or not to[1:].isdigit():
        raise ValueError("Recipient must use E.164 format.")

    if mode == "console":
        if not settings.DEBUG:
            raise ImproperlyConfigured(
                "Console SMS delivery is allowed only in DEBUG mode."
            )

        # Development only: do not expose OTPs in production logs.
        logger.warning(
            "DEVELOPMENT SMS — recipient=%s, message=%s",
            to,
            body,
        )
        return "console-development"

    if mode == "twilio":
        return _send_with_twilio(to, body)

    raise ImproperlyConfigured(
        f"Unsupported SMS_DELIVERY_MODE: {mode}"
    )
