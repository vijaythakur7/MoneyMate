
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
