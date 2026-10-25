from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models import FinancialAccount


@transaction.atomic
def withdraw_money(*, user, account_id, amount):
    amount = Decimal(str(amount))

    if not amount.is_finite() or amount <= Decimal("0.00"):
        raise ValidationError(
            "Withdrawal amount must be a positive, finite number."
        )

    account = (
        FinancialAccount.objects
        .select_for_update()
        .filter(user=user, id=account_id)
        .first()
    )

    if account is None:
        raise ValidationError("Account was not found.")

    if account.balance < amount:
        raise ValidationError("Insufficient funds.")

    account.balance -= amount

    account.save(update_fields=["balance", "updated_at"])

    return account