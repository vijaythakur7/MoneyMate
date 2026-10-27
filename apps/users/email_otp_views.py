from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import EmailOTP, User
from apps.users.tasks import send_email_otp
from django.contrib.auth import get_user_model
from apps.users.models import PendingRegistration
from apps.users.services.email_otp import generate_pending_registration_otp
from apps.users.tasks import send_pending_registration_otp
from django.utils import timezone as django_timezone
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






class VerifyRegistrationOTPAPIView(APIView):
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

        UserModel = get_user_model()

        with transaction.atomic():
            pending = (
                PendingRegistration.objects.select_for_update()
                .filter(email__iexact=email.strip())
                .first()
            )

            if pending is None:
                return Response(
                    {"detail": "Invalid email or OTP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if pending.is_otp_expired():
                return Response(
                    {"detail": "OTP has expired. Request a new code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if pending.otp_attempts >= 5:
                return Response(
                    {"detail": "Too many attempts. Request a new code."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not pending.verify_otp(otp):
                pending.otp_attempts += 1
                pending.save(update_fields=["otp_attempts"])

                return Response(
                    {"detail": "Invalid email or OTP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Recheck uniqueness before creating the actual user.
            if (
                UserModel.objects.filter(
                    email__iexact=pending.email
                ).exists()
                or UserModel.objects.filter(
                    username__iexact=pending.username
                ).exists()
            ):
                return Response(
                    {
                        "detail": (
                            "This email or username is already registered. "
                            "Please contact support if you need assistance."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = UserModel(
                username=pending.username,
                email=pending.email,
                mobile_number=pending.mobile_number,
                currency=pending.currency,
                timezone=pending.timezone,
                is_email_verified=True,
            )

            # The password is already hashed in PendingRegistration.
            user.password = pending.password_hash
            user.save()

            pending.delete()

        return Response(
            {
                "detail": "Registration and email verification successful.",
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )





class ResendRegistrationOTPAPIView(APIView):
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
            pending = (
                PendingRegistration.objects.select_for_update()
                .filter(email__iexact=email.strip())
                .first()
            )

            if pending is not None:
                # Basic cooldown: require at least 60 seconds between sends.
                if (
                    (django_timezone.now() - pending.otp_created_at)
                    .total_seconds() < 60
                ):
                    return Response(
                        {"detail": "Please wait before requesting another OTP."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )

                otp = generate_pending_registration_otp(pending)

                transaction.on_commit(
                    lambda: send_pending_registration_otp.delay(
                        pending.pk,
                        otp,
                    )
                )

        return Response(
            {
                "detail": (
                    "If a pending registration exists, "
                    "a verification code will be sent."
                )
            },
            status=status.HTTP_200_OK,
        )

