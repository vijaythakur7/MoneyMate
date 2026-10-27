
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from apps.users.models import User


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.UserRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "user": "2/min",
        },
    }
)
class AccountThrottlingTests(APITestCase):

    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            username="throttle_test_user",
            email="throttle_test@example.com",
            password="StrongPassword123!",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_is_throttled(self):
        first_response = self.client.get("/api/accounts/")
        second_response = self.client.get("/api/accounts/")
        third_response = self.client.get("/api/accounts/")

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(third_response.status_code, 200)
