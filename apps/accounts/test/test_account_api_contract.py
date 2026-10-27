from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.test.factories import (
    create_test_user,
    create_test_account,
)


class FinancialAccountAPITests(APITestCase):
    def setUp(self):
        self.user = create_test_user(
            username="alice",
            email="alice@example.com",
        )
        self.account = create_test_account(
            user=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_user_can_list_own_accounts(self):
        response = self.client.get("/api/accounts/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )