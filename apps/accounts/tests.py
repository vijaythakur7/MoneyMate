from django.test import TestCase
from rest_framework.test import APIClient
from apps.accounts.models import FinancialAccount
from apps.users.models import User
from apps.accounts.api.serializers import FinancialAccountSerializer

# Create your tests here.

class FinancialAccountIsolationTests(TestCase):

    def setUp(self):
        self.vijay = User.objects.create_user(
            username="vijay",
            email="vijay@example.com",
            password="StrongPassword123!",
        )

        self.rahul = User.objects.create_user(
            username="rahul",
            email="rahul@example.com",
            password="StrongPassword123!",
        )

        self.vijay_account = FinancialAccount.objects.create(
            user=self.vijay,
            name="Vijay Cash Wallet",
            account_type=FinancialAccount.AccountType.CASH,
            balance=5000,
            currency="INR",
        )

        self.rahul_account = FinancialAccount.objects.create(
            user=self.rahul,
            name="Rahul Cash Wallet",
            account_type=FinancialAccount.AccountType.CASH,
            balance=10000,
            currency="INR",
        )

    def test_user_can_access_own_accounts(self):
        accounts = FinancialAccount.objects.filter(
        user=self.vijay,
    )

        self.assertEqual(accounts.count(), 1)
        self.assertEqual(
        accounts.first().pk,
        self.vijay_account.pk,
    )

    def test_user_cannot_access_another_users_account(self):
        accounts = FinancialAccount.objects.filter(
        user=self.vijay,
    )

        self.assertNotIn(
        self.rahul_account,
        accounts,
    )

    def test_user_cannot_retrieve_another_users_account(self):
        account = FinancialAccount.objects.filter(
        id=self.rahul_account.id,
        user=self.vijay,
    ).first()

        self.assertIsNone(account)

    def test_unauthenticated_user_cannot_access_accounts(self):
        response = self.client.get("/accounts/")

        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_access_own_accounts(self):
        self.client.login(
        username="vijay",
        password="StrongPassword123!",
    )

        response = self.client.get("/accounts/")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(
        len(data["accounts"]),
        1,
    )

        self.assertEqual(
        data["accounts"][0]["id"],
        self.vijay_account.id,
    )

    def test_user_cannot_see_another_users_accounts(self):
        self.client.login(
        username="vijay",
        password="StrongPassword123!",
    )

        response = self.client.get("/accounts/")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        account_ids = [
        account["id"]
        for account in data["accounts"]
    ]

        self.assertIn(
        self.vijay_account.id,
        account_ids,
    )

        self.assertNotIn(
        self.rahul_account.id,
        account_ids,
    )

    def test_user_can_view_own_account_detail(self):
        self.client.login(
        username="vijay",
        password="StrongPassword123!",
    )

        response = self.client.get(
        f"/accounts/{self.vijay_account.id}/"
    )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(
        data["id"],
        self.vijay_account.id,
    )

        self.assertEqual(
        data["name"],
        "Vijay Cash Wallet",
    )

    def test_user_cannot_view_another_users_account_detail(self):
        self.client.login(
        username="vijay",
        password="StrongPassword123!",
    )

        response = self.client.get(
        f"/accounts/{self.rahul_account.id}/"
    )

        self.assertEqual(response.status_code, 404)

    def test_user_can_update_own_account(self):
        self.client.login(
        username="vijay",
        password="StrongPassword123!",
    )

        response = self.client.post(
        f"/accounts/{self.vijay_account.id}/",
        {
            "name": "Updated Cash Wallet",
        },
    )

        self.assertEqual(response.status_code, 200)

        self.vijay_account.refresh_from_db()

        self.assertEqual(
        self.vijay_account.name,
        "Updated Cash Wallet",
    )

    def test_user_cannot_update_another_users_account(self):
        self.client.login(
        username="vijay",
        password="StrongPassword123!",
    )

        response = self.client.post(
        f"/accounts/{self.rahul_account.id}/",
        {
            "name": "Hacked Account",
        },
    )

        self.assertEqual(response.status_code, 404)

        self.rahul_account.refresh_from_db()

        self.assertEqual(
        self.rahul_account.name,
        "Rahul Cash Wallet",
    )

    def test_user_cannot_delete_another_users_account(self):
        self.client.login(
        username="vijay",
        password="StrongPassword123!",
    )

        response = self.client.delete(
        f"/accounts/{self.rahul_account.id}/"
    )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
        FinancialAccount.objects.filter(
            id=self.rahul_account.id
        ).exists()
    )

    def test_user_can_delete_own_account(self):
        self.client.login(
        username="vijay",
        password="StrongPassword123!",
    )

        response = self.client.delete(
        f"/accounts/{self.vijay_account.id}/"
    )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
        FinancialAccount.objects.filter(
            id=self.vijay_account.id
        ).exists()
    )

    def test_financial_account_serializer(self):
        serializer = FinancialAccountSerializer(
        self.vijay_account
    )

        self.assertEqual(
        serializer.data["id"],
        self.vijay_account.id,
    )

        self.assertEqual(
        serializer.data["name"],
        "Vijay Cash Wallet",
    )

        self.assertEqual(
        serializer.data["account_type"],
        "CASH",
    )

        self.assertEqual(
        serializer.data["currency"],
        "INR",
    )

    def test_serializer_rejects_empty_account_name(self):
        serializer = FinancialAccountSerializer(
        data={
            "name": "",
            "account_type": "CASH",
            "balance": "5000.00",
            "currency": "INR",
        }
    )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
        "name",
        serializer.errors,
    )

    def test_authenticated_user_can_list_own_accounts(self):
        client = APIClient()

        client.force_authenticate(
        user=self.vijay
    )

        response = client.get(
        "/api/accounts/"
    )

        self.assertEqual(
        response.status_code,
        200,
    )

        self.assertEqual(
        len(response.data["accounts"]),
        1,
    )

        self.assertEqual(
        response.data["accounts"][0]["id"],
        self.vijay_account.id,
    )

    def test_user_cannot_see_another_users_accounts_through_api(self):
        client = APIClient()

        client.force_authenticate(
        user=self.vijay
    )

        response = client.get(
        "/api/accounts/"
    )

        self.assertEqual(
        response.status_code,
        200,
    )

        account_ids = [
        account["id"]
        for account in response.data["accounts"]
    ]

        self.assertIn(
        self.vijay_account.id,
        account_ids,
    )

        self.assertNotIn(
        self.rahul_account.id,
        account_ids,
    )

    def test_unauthenticated_user_cannot_list_accounts_through_api(self):
        client = APIClient()

        response = client.get(
        "/api/accounts/"
    )

        self.assertEqual(
        response.status_code,
        403,
    )