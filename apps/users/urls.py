from django.urls import path

from apps.users.views import UserRegistrationAPIView
from apps.users.email_otp_views import VerifyEmailOTPAPIView
from apps.users.email_otp_views import ResendEmailOTPAPIView

urlpatterns = [
    path(
        "auth/register/",
        UserRegistrationAPIView.as_view(),
        name="api-user-register",
    ),

    path(
    "verify-email-otp/",
    VerifyEmailOTPAPIView.as_view(),
    name="verify-email-otp",
),

    path(
    "resend-email-otp/",
    ResendEmailOTPAPIView.as_view(),
    name="resend-email-otp",
),
]
