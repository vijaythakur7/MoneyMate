
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from apps.users.models import PendingRegistration, User
from apps.users.services.email_otp import (
    generate_email_otp,
    generate_pending_registration_otp,
)

import logging

from django.core.exceptions import ImproperlyConfigured
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from apps.users.services.sms_adapter import send_sms
from apps.users.services.mobile_otp import generate_mobile_otp



@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_email_otp(user_id):
    """Send an OTP to an existing, unverified user."""
    user = User.objects.get(pk=user_id)

    if user.is_email_verified:
        return "Email already verified"

    otp = generate_email_otp(user)

    send_mail(
        subject="Your MoneyMate verification code",
        message=(
            f"Hello {user.username},\n\n"
            f"Your MoneyMate email verification code is: {otp}\n\n"
            "This code expires in 5 minutes.\n"
            "If you did not request this code, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return "Email OTP sent"


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_pending_registration_otp(pending_registration_id):
    """Generate and send an OTP for a pending registration."""
    pending = PendingRegistration.objects.get(
        pk=pending_registration_id,
    )

    otp = generate_pending_registration_otp(pending)

    send_mail(
        subject="Your MoneyMate registration verification code",
        message=(
            f"Hello {pending.username},\n\n"
            f"Your MoneyMate registration code is: {otp}\n\n"
            "This code expires in 5 minutes.\n"
            "If you did not request this code, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[pending.email],
        fail_silently=False,
    )

    return "Pending registration OTP sent"




@shared_task
def send_mobile_otp(user_id):
    """Generate a mobile OTP and request SMS delivery."""
    user = User.objects.get(pk=user_id)

    if user.is_mobile_verified:
        return "Mobile already verified"

    if not user.mobile_number:
        raise ValueError("User has no registered mobile number.")

    mobile_number = user.mobile_number.strip()

    if (
        not mobile_number.startswith("+")
        or not mobile_number[1:].isdigit()
        or not 8 <= len(mobile_number[1:]) <= 15
    ):
        raise ValueError(
            "Store the mobile number in E.164 format, "
            "for example +91XXXXXXXXXX."
        )

    otp = generate_mobile_otp(user)

    message_sid = send_sms(
        to=mobile_number,
        body=(
            f"Your MoneyMate verification code is {otp}. "
            "It expires in 5 minutes. Do not share this code."
        ),
    )

    return f"Mobile OTP delivery submitted: {message_sid}"
