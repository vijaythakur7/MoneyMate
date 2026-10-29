
# Create your views here.
from django.db import transaction
from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.users.serializers import UserRegistrationSerializer

from django.contrib.auth.hashers import make_password
from datetime import timedelta
from django.utils import timezone
from apps.users.models import PendingRegistration, User
from apps.users.services.email_otp import generate_pending_registration_otp
from apps.users.tasks import send_pending_registration_otp

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.tasks import send_mobile_otp
from apps.users.services.mobile_otp import verify_mobile_otp



def hello(request):
    print("Method:", request.method)
    print("Path:", request.path)
    return HttpResponse("Hello from MoneyMate!")

@extend_schema(
    summary="Get user detail",
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="User ID",
        )
    ],
    responses={200: OpenApiTypes.STR},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def user_detail(request, id):
    return HttpResponse(f"User ID: {id}")

@extend_schema(
    summary="Search",
    parameters=[
        OpenApiParameter(
            name="q",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search query",
        )
    ],
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def search(request):
    query = request.GET.get("q")

    return HttpResponse(f"Search query: {query}")

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework.views import APIView


class HelloAPIView(APIView):

    def get(self, request):
        return Response({
            "message": "Hello from MoneyMate API"
        })

@extend_schema(
    summary="User login",
    description=(
        "Authenticates a user with their username and password. "
        "On success, creates a Django session."
    ),
    request={
        "application/x-www-form-urlencoded": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string", "format": "password"},
            },
            "required": ["username", "password"],
        }
    },
    responses={
        200: OpenApiTypes.OBJECT,
        401: OpenApiResponse(description="Invalid username or password."),
        403: OpenApiResponse(description="CSRF verification failed."),
    },
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def login_view(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return JsonResponse(
            {"detail": "Invalid username or password."},
            status=401,
        )

    login(request, user)

    return JsonResponse(
        {"detail": "Login successful."},
        status=200,
    )
@extend_schema(
    summary="User logout",
    description="Logs out the current user and clears their Django session.",
    request=None,
    responses={
        200: OpenApiTypes.OBJECT,
        403: OpenApiResponse(description="Authentication or CSRF verification failed."),
    },
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)

    return JsonResponse(
        {"detail": "Logout successful."},
        status=200,
    )

@extend_schema(
    summary="Get CSRF token",
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def csrf_token_view(request):
    token = get_token(request)

    return JsonResponse({
        "csrfToken": token,
    })

from apps.users.tasks import send_email_otp



class UserRegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data.copy()

        password = data.pop("password")
        data.pop("password_confirm", None)

        # Check that an existing account doesn't already use these details.
        if User.objects.filter(email__iexact=data["email"]).exists():
            return Response(
                {"email": ["A user with this email already exists."]},
                status=400,
            )

        if User.objects.filter(username__iexact=data["username"]).exists():
            return Response(
                {"username": ["A user with this username already exists."]},
                status=400,
            )

        with transaction.atomic():
            # Replace any earlier pending registration for this email.
            PendingRegistration.objects.filter(
                email__iexact=data["email"],
            ).delete()

            # Also prevent a username from being pending for another email.
            PendingRegistration.objects.filter(
                username__iexact=data["username"],
            ).delete()

            pending = PendingRegistration.objects.create(
                **data,
                password_hash=make_password(password),
                otp_hash="pending",
                otp_expires_at=timezone.now() + timedelta(minutes=5),
            )

            # Generate and save the OTP before queuing the email.
            otp = generate_pending_registration_otp(pending)

            transaction.on_commit(
                lambda: send_pending_registration_otp.delay(
                    pending.pk,
                )
            )

        return Response(
            {
                "detail": (
                    "Registration started. Check your email "
                    "for the verification code."
                ),
                "email": pending.email,
            },
            status=201,
        )






# class RequestMobileOTPAPIView(APIView):
#     """Request mobile OTP delivery for the authenticated user."""

#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user

#         if user.is_mobile_verified:
#             return Response(
#                 {"detail": "Mobile number is already verified."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if not user.mobile_number or not user.mobile_number.strip():
#             return Response(
#                 {"detail": "Register a mobile number first."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         transaction.on_commit(
#             lambda: send_mobile_otp.delay(user.pk)
#         )

#         return Response(
#             {
#                 "detail": (
#                     "Mobile OTP delivery request queued. "
#                     "SMS delivery is not yet confirmed."
#                 )
#             },
#             status=status.HTTP_202_ACCEPTED,
#         )
import logging

from apps.users.services.twilio_verify import check_verification_code

logger = logging.getLogger(__name__)



class VerifyMobileOTPAPIView(APIView):
    """Verify a mobile code using Twilio Verify."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_mobile_verified:
            return Response(
                {"detail": "Mobile number is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mobile_number = (user.mobile_number or "").strip()
        if not mobile_number:
            return Response(
                {"detail": "Register a mobile number first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "otp" not in request.data:
            return Response(
                {"otp": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = request.data["otp"]

        try:
            approved = check_verification_code(mobile_number, otp)
        except Exception:
            logger.exception(
                "Twilio Verify check failed for user_id=%s",
                user.pk,
            )
            return Response(
                {"detail": "Unable to verify the code right now."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not approved:
            return Response(
                {"detail": "Invalid or expired verification code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_mobile_verified = True
        user.save(update_fields=["is_mobile_verified"])

        return Response(
            {"detail": "Mobile number verified successfully."},
            status=status.HTTP_200_OK,
        )



from apps.users.services.twilio_verify import send_verification_code


class RequestMobileOTPAPIView(APIView):
    """Request a real SMS verification code through Twilio Verify."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_mobile_verified:
            return Response(
                {"detail": "Mobile number is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mobile_number = (user.mobile_number or "").strip()

        if not mobile_number:
            return Response(
                {"detail": "Register a mobile number first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            twilio_status = send_verification_code(mobile_number)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            # Log the full exception on the server, not in the API response.
            import logging
            logging.getLogger(__name__).exception(
                "Unable to start Twilio Verify for user_id=%s",
                user.pk,
            )
            return Response(
                {"detail": "Unable to send the verification code right now."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if twilio_status != "pending":
            return Response(
                {"detail": "Twilio did not start the verification request."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {"detail": "Verification code sent by SMS."},
            status=status.HTTP_200_OK,
        )
