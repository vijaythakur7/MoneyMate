from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.users.models import User
from apps.accounts.models import FinancialAccount
from apps.accounts.services.transfers import transfer_money


class TransferMoneyTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="transferuser",
            email="transfer@example.com",
            password="StrongTestPass123!",
        )

        self.source = FinancialAccount.objects.create(
            user=self.user,
            name="Savings",
            account_type="SAVINGS",
            balance=Decimal("10000.00"),
            currency="INR",
        )

        self.destination = FinancialAccount.objects.create(
            user=self.user,
            name="Cash",
            account_type="CASH",
            balance=Decimal("2000.00"),
            currency="INR",
        )

    def test_successful_transfer_updates_both_balances(self):
        transfer_money(
            user=self.user,
            from_account_id=self.source.id,
            to_account_id=self.destination.id,
            amount=Decimal("1000.00"),
        )

        self.source.refresh_from_db()
        self.destination.refresh_from_db()

        self.assertEqual(
            self.source.balance,
            Decimal("9000.00"),
        )
        self.assertEqual(
            self.destination.balance,
            Decimal("3000.00"),
        )

    def test_insufficient_funds_rejects_transfer(self):
        with self.assertRaises(ValidationError):
            transfer_money(
                user=self.user,
                from_account_id=self.source.id,
                to_account_id=self.destination.id,
                amount=Decimal("20000.00"),
            )

        self.source.refresh_from_db()
        self.destination.refresh_from_db()

        self.assertEqual(
            self.source.balance,
            Decimal("10000.00"),
        )
        self.assertEqual(
            self.destination.balance,
            Decimal("2000.00"),
        )