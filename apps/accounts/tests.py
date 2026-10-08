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

    def test_authenticated_user_can_create_account(self):
        client = APIClient()

        client.force_authenticate(
        user=self.vijay
    )

        response = client.post(
        "/api/accounts/",
        {
            "name": "HDFC Bank",
            "account_type": "BANK",
            "balance": "25000.00",
            "currency": "INR",
        },
        format="json",
    )

        self.assertEqual(
        response.status_code,
        201,
    )

        self.assertEqual(
        response.data["name"],
        "HDFC Bank",
    )

        self.assertEqual(
        response.data["account_type"],
        "BANK",
    )

        self.assertEqual(
        response.data["currency"],
        "INR",
    )

        account = FinancialAccount.objects.get(
        name="HDFC Bank",
    )

        self.assertEqual(
        account.user,
        self.vijay,
    )

    def test_unauthenticated_user_cannot_create_account(self):
        client = APIClient()

        response = client.post(
        "/api/accounts/",
        {
            "name": "Unauthorized Account",
            "account_type": "BANK",
            "balance": "1000.00",
            "currency": "INR",
        },
        format="json",
    )

        self.assertEqual(
        response.status_code,
        403,
    )

    def test_create_account_rejects_invalid_account_type(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.post(
            "/api/accounts/",
            {
                "name": "Invalid Account",
                "account_type": "INVALID",
                "balance": "1000.00",
                "currency": "INR",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "account_type",
            response.data,
        )

    def test_create_account_ignores_client_user(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.post(
            "/api/accounts/",
            {
                "name": "Client User Attempt",
                "account_type": "BANK",
                "balance": "1000.00",
                "currency": "INR",
                "user": self.rahul.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        account = FinancialAccount.objects.get(
            name="Client User Attempt",
        )

        self.assertEqual(
            account.user,
            self.vijay,
        )

        self.assertNotEqual(
            account.user,
            self.rahul,
        )

    def test_create_account_rejects_empty_name(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.post(
            "/api/accounts/",
            {
                "name": "",
                "account_type": "BANK",
                "balance": "25000.00",
                "currency": "INR",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "name",
            response.data,
        )

### User can view own account  ####
    def test_authenticated_user_can_view_own_account_through_api(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.get(
            f"/api/accounts/{self.vijay_account.id}/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["id"],
            self.vijay_account.id,
        )

        self.assertEqual(
            response.data["name"],
            "Vijay Cash Wallet",
        )

###  Cannot View Rahul's Account  ###

    def test_user_cannot_view_another_users_account_through_api(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.get(
            f"/api/accounts/{self.rahul_account.id}/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

###   Unauthenticated Detail ###

    def test_unauthenticated_user_cannot_view_account_through_api(self):
        client = APIClient()

        response = client.get(
            f"/api/accounts/{self.vijay_account.id}/"
        )

        self.assertEqual(
            response.status_code,
            403,
        )

###  User Can PUT Own Account  ###

    def test_authenticated_user_can_put_own_account(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.put(
            f"/api/accounts/{self.vijay_account.id}/",
            {
                "name": "HDFC Salary Account",
                "account_type": "BANK",
                "balance": "30000.00",
                "currency": "INR",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.vijay_account.refresh_from_db()

        self.assertEqual(
            self.vijay_account.name,
            "HDFC Salary Account",
        )

        self.assertEqual(
            self.vijay_account.account_type,
            "BANK",
        )


### User Can PATCH Own Account   ###

    def test_authenticated_user_can_patch_own_account(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.patch(
            f"/api/accounts/{self.vijay_account.id}/",
            {
                "name": "Updated Wallet",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.vijay_account.refresh_from_db()

        self.assertEqual(
            self.vijay_account.name,
            "Updated Wallet",
        )

        self.assertEqual(
            self.vijay_account.account_type,
            "CASH",
        )

###   Cannot PUT Rahul's Account  ###

    def test_user_cannot_put_another_users_account(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.put(
            f"/api/accounts/{self.rahul_account.id}/",
            {
                "name": "Hacked Account",
                "account_type": "BANK",
                "balance": "999999.00",
                "currency": "INR",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.rahul_account.refresh_from_db()

        self.assertEqual(
            self.rahul_account.name,
            "Rahul Cash Wallet",
        )

###   Cannot PATCH Rahul's Account   ###

    def test_user_cannot_patch_another_users_account(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.patch(
            f"/api/accounts/{self.rahul_account.id}/",
            {
                "name": "Hacked Account",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.rahul_account.refresh_from_db()

        self.assertEqual(
            self.rahul_account.name,
            "Rahul Cash Wallet",
        )

###  User can delete own account  ###

    def test_authenticated_user_can_delete_own_account(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.delete(
            f"/api/accounts/{self.vijay_account.id}/"
        )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            FinancialAccount.objects.filter(
                id=self.vijay_account.id
            ).exists()
        )

###   Test another user's account   ###

    def test_user_cannot_delete_another_users_account(self):
        client = APIClient()

        client.force_authenticate(
            user=self.vijay
        )

        response = client.delete(
            f"/api/accounts/{self.rahul_account.id}/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertTrue(
            FinancialAccount.objects.filter(
                id=self.rahul_account.id
            ).exists()
        )

###   Test unauthenticated DELETE   ###

    def test_unauthenticated_user_cannot_delete_account(self):
        client = APIClient()

        response = client.delete(
            f"/api/accounts/{self.vijay_account.id}/"
        )

        self.assertEqual(
            response.status_code,
            403,
        )