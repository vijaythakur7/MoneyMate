from django.urls import path

from apps.users.email_otp_views import (
    ResendEmailOTPAPIView,
    VerifyEmailOTPAPIView,
    ResendRegistrationOTPAPIView,
    VerifyRegistrationOTPAPIView,
)
from apps.users.views import UserRegistrationAPIView

urlpatterns = [
    path(
        "auth/register/",
        UserRegistrationAPIView.as_view(),
        name="api-user-register",
    ),
    path(
        "auth/verify-registration-otp/",
        VerifyRegistrationOTPAPIView.as_view(),
        name="verify-registration-otp",
    ),
    path(
        "auth/resend-registration-otp/",
        ResendRegistrationOTPAPIView.as_view(),
        name="resend-registration-otp",
    ),
    path(
        "auth/verify-email-otp/",
        VerifyEmailOTPAPIView.as_view(),
        name="verify-email-otp",
    ),
    path(
        "auth/resend-email-otp/",
        ResendEmailOTPAPIView.as_view(),
        name="resend-email-otp",
    ),
]