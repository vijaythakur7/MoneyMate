from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.models import User, EmailOTP
from apps.users.tasks import send_email_otp


MAX_OTP_ATTEMPTS = 5


class VerifyEmailOTPAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not isinstance(email, str) or not email.strip():
            return Response(
                {"detail": "A valid email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not isinstance(otp, str)
            or len(otp) != 6
            or not otp.isdigit()
        ):
            return Response(
                {"detail": "OTP must be a 6-digit code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            user = User.objects.select_for_update().filter(
                email__iexact=email.strip()
            ).first()

            if user is None:
                return Response(
                    {"detail": "Invalid email or OTP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if user.is_email_verified:
                return Response(
                    {"detail": "Email is already verified."},
                    status=status.HTTP_200_OK,
                )

            otp_record = (
                EmailOTP.objects.select_for_update()
                .filter(user=user, is_used=False)
                .order_by("-created_at")
                .first()
            )

            if otp_record is None:
                return Response(
                    {"detail": "No active OTP. Request a new code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if otp_record.is_expired():
                otp_record.is_used = True
                otp_record.save(update_fields=["is_used"])

                return Response(
                    {"detail": "OTP has expired. Request a new code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if otp_record.attempts >= MAX_OTP_ATTEMPTS:
                return Response(
                    {"detail": "Too many attempts. Request a new code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not otp_record.verify_otp(otp):
                otp_record.attempts += 1

                if otp_record.attempts >= MAX_OTP_ATTEMPTS:
                    otp_record.is_used = True

                otp_record.save(
                    update_fields=["attempts", "is_used"]
                )

                return Response(
                    {"detail": "Invalid email or OTP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            otp_record.is_used = True
            otp_record.save(update_fields=["is_used"])

            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])

        return Response(
            {"detail": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )


class ResendEmailOTPAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not isinstance(email, str) or not email.strip():
            return Response(
                {"detail": "A valid email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            user = User.objects.select_for_update().filter(
                email__iexact=email.strip()
            ).first()

            if user is None:
                return Response(
                    {"detail": "If the account exists, a new OTP will be sent."},
                    status=status.HTTP_200_OK,
                )

            if user.is_email_verified:
                return Response(
                    {"detail": "Email is already verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            transaction.on_commit(
                lambda: send_email_otp.delay(user.pk)
            )

        return Response(
            {"detail": "If the account exists, a new OTP will be sent."},
            status=status.HTTP_200_OK,
        )