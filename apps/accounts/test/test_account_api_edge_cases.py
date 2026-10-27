from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import FinancialAccount

User = get_user_model()


class FinancialAccountEdgeCaseTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        self.accounts_url = "/api/accounts/"

    def test_blank_account_name_is_rejected(self):
        payload = {
            "name": "   ",
            "account_type": "CASH",
            "balance": "100.00",
            "currency": "INR",
        }

        response = self.client.post(
            self.accounts_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            FinancialAccount.objects.filter(user=self.user).exists()
        )

    def test_invalid_account_type_is_rejected(self):
        payload = {
            "name": "My Account",
            "account_type": "INVALID_TYPE",
            "balance": "100.00",
            "currency": "INR",
        }

        response = self.client.post(
            self.accounts_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            FinancialAccount.objects.filter(user=self.user).exists()
        )


    def test_user_cannot_see_another_users_account(self):
        another_user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="TestPassword123!",
        )

        FinancialAccount.objects.create(
            user=another_user,
            name="Bob Savings",
            account_type=FinancialAccount.AccountType.SAVINGS,
            balance=Decimal("5000.00"),
            currency="INR",
        )

        response = self.client.get(self.accounts_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertNotContains(response, "Bob Savings")

    def test_user_cannot_retrieve_another_users_account_by_id(self):
        another_user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="TestPassword123!",
        )

        other_account = FinancialAccount.objects.create(
            user=another_user,
            name="Bob Savings",
            account_type=FinancialAccount.AccountType.SAVINGS,
            balance=Decimal("5000.00"),
            currency="INR",
        )

        response = self.client.get(
            f"{self.accounts_url}{other_account.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


    def test_duplicate_account_name_is_rejected(self):
        FinancialAccount.objects.create(
            user=self.user,
            name="Main Cash",
            account_type=FinancialAccount.AccountType.CASH,
            balance=Decimal("100.00"),
            currency="INR",
        )

        payload = {
            "name": "Main Cash",
            "account_type": "CASH",
            "balance": "200.00",
            "currency": "INR",
        }

        response = self.client.post(
            self.accounts_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            FinancialAccount.objects.filter(
                user=self.user,
                name="Main Cash",
            ).count(),
            1,
        )

    def test_client_cannot_assign_account_to_another_user(self):
        another_user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="TestPassword123!",
        )

        payload = {
            "name": "My New Account",
            "account_type": "CASH",
            "balance": "100.00",
            "currency": "INR",
            "user": another_user.id,
        }

        response = self.client.post(
            self.accounts_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        account = FinancialAccount.objects.get(
            user=self.user,
            name="My New Account",
        )

        self.assertEqual(account.user_id, self.user.id)
        self.assertNotEqual(account.user_id, another_user.id)



    def test_anonymous_user_cannot_list_accounts(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.accounts_url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )