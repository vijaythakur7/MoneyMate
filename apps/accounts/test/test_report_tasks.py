from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class MonthlyReportAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reportuser",
            email="report@example.com",
            password="TestPassword123!",
        )

    @patch("apps.accounts.api.views.generate_monthly_report.delay")
    def test_authenticated_user_can_queue_report(self, mock_delay):
        mock_delay.return_value.id = "test-task-123"
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/api/reports/monthly/")

        self.assertEqual(
            response.status_code,
            status.HTTP_202_ACCEPTED,
        )
        self.assertEqual(response.data["task_id"], "test-task-123")
        mock_delay.assert_called_once_with(self.user.pk)

    def test_anonymous_user_cannot_queue_report(self):
        response = self.client.post("/api/reports/monthly/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )