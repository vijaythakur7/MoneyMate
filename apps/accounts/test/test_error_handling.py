
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from apps.users.models import User


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework_simplejwt.authentication.JWTAuthentication",
            "rest_framework.authentication.SessionAuthentication",
        ],
        "EXCEPTION_HANDLER": (
            "common.exceptions.custom_exception_handler"
        ),
    }
)
class AccountErrorHandlingTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="error_test_user",
            email="error_test@example.com",
            password="StrongPassword123!",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_invalid_account_type_returns_standard_error(self):
        response = self.client.post(
            "/api/accounts/",
            {
                "name": "Test Account",
                "account_type": "INVALID",
                "balance": "100.00",
                "currency": "INR",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"]["code"],
            "validation_error",
        )
        self.assertIn(
            "account_type",
            response.data["error"]["details"],
        )
