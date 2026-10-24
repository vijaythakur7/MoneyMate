from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


class AccountVersioningTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="versionuser",
            email="versionuser@example.com",
            password="StrongTestPass123!",
        )

        access_token = str(
            RefreshToken.for_user(self.user).access_token
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

    def test_v1_accounts_endpoint_is_available(self):
        response = self.client.get("/api/v1/accounts/")
        self.assertEqual(response.status_code, 200)

    def test_v2_accounts_endpoint_is_available(self):
        response = self.client.get("/api/v2/accounts/")
        self.assertEqual(response.status_code, 200)

    def test_unsupported_version_is_rejected(self):
        response = self.client.get("/api/v3/accounts/")
        self.assertEqual(response.status_code, 404)