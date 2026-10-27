from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import close_old_connections
from django.test import TransactionTestCase

from apps.accounts.models import FinancialAccount
from apps.accounts.services.withdrawals import withdraw_money

User = get_user_model()


class WithdrawalTests(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="withdrawuser",
            email="withdraw@example.com",
            password="TestPassword123!",
        )

        self.account = FinancialAccount.objects.create(
            user=self.user,
            name="Cash Account",
            account_type=FinancialAccount.AccountType.CASH,
            balance=Decimal("1000.00"),
            currency="INR",
        )

    def test_successful_withdrawal(self):
        withdraw_money(
            user=self.user,
            account_id=self.account.id,
            amount="200.00",
        )

        self.account.refresh_from_db()

        self.assertEqual(
            self.account.balance,
            Decimal("800.00"),
        )

    def test_withdrawal_rejects_insufficient_funds(self):
        with self.assertRaises(ValidationError):
            withdraw_money(
                user=self.user,
                account_id=self.account.id,
                amount="1200.00",
            )

        self.account.refresh_from_db()

        self.assertEqual(
            self.account.balance,
            Decimal("1000.00"),
        )

    def test_concurrent_withdrawals_do_not_overdraw(self):
        account_id = self.account.id
        user_id = self.user.id
        start_barrier = Barrier(2)

        def attempt_withdrawal():
            close_old_connections()
            try:
                user = User.objects.get(pk=user_id)
                start_barrier.wait(timeout=10)

                try:
                    withdraw_money(
                        user=user,
                        account_id=account_id,
                        amount="800.00",
                    )
                    return "success"
                except ValidationError:
                    return "rejected"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(attempt_withdrawal)
                for _ in range(2)
            ]
            results = [future.result(timeout=30) for future in futures]

        self.account.refresh_from_db()

        self.assertCountEqual(results, ["success", "rejected"])
        self.assertEqual(
            self.account.balance,
            Decimal("200.00"),
        )