from django.test import Client, TestCase

# Create your tests here.

from django.contrib.auth import authenticate
from apps.users.models import User
from django.contrib.auth import login


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

    def test_user_can_register(self):
        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            User.objects.filter(
                username="newuser"
            ).exists()
        )
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirm", response.data)

    def test_password_is_hashed(self):
        self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        user = User.objects.get(username="newuser")

        self.assertNotEqual(
            user.password,
            self.payload["password"],
        )
        self.assertTrue(
            user.check_password(self.payload["password"])
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
        self.assertIn("email", response.data)

    def test_mismatched_passwords_are_rejected(self):
        self.payload["password_confirm"] = "Different!Password_92"

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password_confirm", response.data)

    def test_weak_password_is_rejected(self):
        self.payload["password"] = "123"
        self.payload["password_confirm"] = "123"

        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)