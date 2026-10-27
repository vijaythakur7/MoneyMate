from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from apps.users.models import User

# from apps.users.services.email_verification import (
#     generate_verification_token,
# )
from apps.users.services.email_otp import generate_email_otp


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_email_otp(user_id):
    user = User.objects.get(pk=user_id)

    if user.is_email_verified:
        return "Email already verified"

    otp = generate_email_otp(user)


    print("SMTP HOST:", settings.EMAIL_HOST)
    print("SMTP PORT:", settings.EMAIL_PORT)
    print("SMTP USER:", settings.EMAIL_HOST_USER)
    print("SMTP PASSWORD LENGTH:", len(settings.EMAIL_HOST_PASSWORD))
    print("SMTP TLS:", settings.EMAIL_USE_TLS)

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