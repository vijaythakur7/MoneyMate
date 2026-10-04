from django.db import models

# Create your models here.
from django.conf import settings


class FinancialAccount(models.Model):

    class AccountType(models.TextChoices):
        BANK = "BANK", "Bank Account"
        CASH = "CASH", "Cash"
        CREDIT_CARD = "CREDIT_CARD", "Credit Card"
        SAVINGS = "SAVINGS", "Savings Account"
        INVESTMENT = "INVESTMENT", "Investment"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="financial_accounts",
    )

    name = models.CharField(
        max_length=100,
    )

    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
    )

    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    currency = models.CharField(
        max_length=3,
        default="INR",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_account_name_per_user",
            ),
        ]

    def __str__(self):
        return self.name