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