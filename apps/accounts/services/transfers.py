from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from apps.accounts.models import FinancialAccount


@transaction.atomic
def transfer_money(
    *,
    user,
    from_account_id,
    to_account_id,
    amount,
):
    amount = Decimal(str(amount))

    if amount <= Decimal("0.00"):
        raise ValidationError(
            "Transfer amount must be greater than zero."
        )

    if from_account_id == to_account_id:
        raise ValidationError(
            "Source and destination accounts must differ."
        )

    accounts = list(
        FinancialAccount.objects
        .select_for_update()
        .filter(
            user=user,
            id__in=[from_account_id, to_account_id],
        )
        .order_by("id")
    )

    account_by_id = {account.id: account for account in accounts}

    if len(accounts) != 2:
        raise ValidationError(
            "One or both accounts were not found."
        )

    source = account_by_id[from_account_id]
    destination = account_by_id[to_account_id]

    if source.currency != destination.currency:
        raise ValidationError(
            "Accounts must use the same currency."
        )

    if source.balance < amount:
        raise ValidationError(
            "Insufficient funds."
        )

    source.balance -= amount
    destination.balance += amount

    source.save(update_fields=["balance", "updated_at"])
    destination.save(update_fields=["balance", "updated_at"])

    return source, destination