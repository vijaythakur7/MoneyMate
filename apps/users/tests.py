# Create your tests here.
from django.contrib.auth import authenticate
from django.test import Client, TestCase
from django.contrib.auth.hashers import identify_hasher
from apps.users.models import PendingRegistration
# from apps.users.models import User
from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.users.models import PendingRegistration
from apps.users.email_otp_views import VerifyRegistrationOTPAPIView

class UserAuthenticationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPassword123!",
        )
        self.client = Client()

    def test_user_can_authenticate_with_valid_credentials(self):
        authenticated_user = authenticate(
            username="testuser",
            password="StrongPassword123!",
        )

        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.pk, self.user.pk)

    def test_user_cannot_authenticate_with_invalid_password(self):
        authenticated_user = authenticate(
            username="testuser",
            password="WrongPassword123!",
    )

        self.assertIsNone(authenticated_user)

    def test_unknown_user_cannot_authenticate(self):
        authenticated_user = authenticate(
        username="unknownuser",
        password="StrongPassword123!",
    )

        self.assertIsNone(authenticated_user)

    def test_inactive_user_cannot_authenticate(self):
        self.user.is_active = False
        self.user.save()

        authenticated_user = authenticate(
            username="testuser",
            password="StrongPassword123!",
        )

        self.assertIsNone(authenticated_user)

    def test_user_can_login_with_valid_credentials(self):
        response = self.client.post(
        "/auth/login/",
        {
            "username": "testuser",
            "password": "StrongPassword123!",
        },
    )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
        response.wsgi_request.user.is_authenticated
    )

        self.assertEqual(
        response.json()["detail"],
        "Login successful.",
    )

    def test_user_cannot_login_with_invalid_credentials(self):
        response = self.client.post(
        "/auth/login/",
        {
            "username": "testuser",
            "password": "WrongPassword123!",
        },
    )

        self.assertEqual(response.status_code, 401)

        self.assertFalse(
        response.wsgi_request.user.is_authenticated
    )

    def test_authenticated_user_can_logout(self):
        self.client.login(
        username="testuser",
        password="StrongPassword123!",
    )

        response = self.client.post("/auth/logout/")

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
        response.wsgi_request.user.is_authenticated
    )

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegistrationAPITests(APITestCase):
    url = "/api/auth/register/"

    def setUp(self):
        self.payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "River!Stone_82#Cloud",
            "password_confirm": "River!Stone_82#Cloud",
            "mobile_number": "9876543210",
            "currency": "INR",
            "timezone": "Asia/Kolkata",
        }


    def test_registration_creates_pending_record_not_user(self):
        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertFalse(
            User.objects.filter(username="newuser").exists()
        )

        self.assertTrue(
            PendingRegistration.objects.filter(
                username="newuser",
                email="newuser@example.com",
            ).exists()
        )

        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirm", response.data)


    def test_pending_registration_password_is_hashed(self):
        self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        pending = PendingRegistration.objects.get(
            username="newuser"
        )

        self.assertNotEqual(
            pending.password_hash,
            self.payload["password"],
        )

        password_hasher = identify_hasher(pending.password_hash)
        self.assertIsNotNone(password_hasher)

        self.assertTrue(
            password_hasher.verify(
                self.payload["password"],
                pending.password_hash,
            )
        )


    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="existinguser",
            email="newuser@example.com",
            password="Another!Secure_92#Password",
        )

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email",response.data["error"]["details"],)

    def test_mismatched_passwords_are_rejected(self):
        self.payload["password_confirm"] = "Different!Password_92"

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password_confirm", response.data["error"]["details"],)

    def test_weak_password_is_rejected(self):
        self.payload["password"] = "123"
        self.payload["password_confirm"] = "123"

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data["error"]["details"],)




class RegistrationOTPVerificationTests(APITestCase):
    verify_url = "/api/auth/verify-registration-otp/"

    def setUp(self):
        self.password = "River!Stone_82#Cloud"
        self.otp = "123456"

        from django.contrib.auth.hashers import make_password

        self.pending = PendingRegistration.objects.create(
            username="otpuser",
            email="otpuser@example.com",
            password_hash=make_password(self.password),
            mobile_number="9876543210",
            currency="INR",
            timezone="Asia/Kolkata",
            otp_hash="",
            otp_expires_at=timezone.now() + timedelta(minutes=5),
        )

        # Use the same HMAC hashing approach as the model.
        import hashlib
        import hmac
        from django.conf import settings

        self.pending.otp_hash = hmac.new(
            settings.SECRET_KEY.encode(),
            self.otp.encode(),
            hashlib.sha256,
        ).hexdigest()
        self.pending.save(update_fields=["otp_hash"])

    def test_valid_otp_creates_user_and_deletes_pending_record(self):
        response = self.client.post(
            self.verify_url,
            {"email": self.pending.email, "otp": self.otp},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(username="otpuser").exists()
        )
        self.assertFalse(
            PendingRegistration.objects.filter(
                email="otpuser@example.com"
            ).exists()
        )

        user = User.objects.get(username="otpuser")
        self.assertTrue(user.is_email_verified)
        self.assertTrue(user.check_password(self.password))

    def test_invalid_otp_does_not_create_user(self):
        response = self.client.post(
            self.verify_url,
            {"email": self.pending.email, "otp": "000000"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            User.objects.filter(username="otpuser").exists()
        )
        self.assertEqual(
            PendingRegistration.objects.get(pk=self.pending.pk).otp_attempts,
            1,
        )

    def test_expired_otp_does_not_create_user(self):
        self.pending.otp_expires_at = timezone.now() - timedelta(minutes=1)
        self.pending.save(update_fields=["otp_expires_at"])

        response = self.client.post(
            self.verify_url,
            {"email": self.pending.email, "otp": self.otp},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            User.objects.filter(username="otpuser").exists()
        )

    def test_five_failed_attempts_block_verification(self):
        self.pending.otp_attempts = 5
        self.pending.save(update_fields=["otp_attempts"])

        response = self.client.post(
            self.verify_url,
            {"email": self.pending.email, "otp": self.otp},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            User.objects.filter(username="otpuser").exists()
        )
