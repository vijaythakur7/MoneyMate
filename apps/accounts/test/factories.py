import factory
from django.contrib.auth import get_user_model

from apps.accounts.models import FinancialAccount

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(
        lambda n: f"testuser{n}"
    )
    email = factory.LazyAttribute(
        lambda obj: f"{obj.username}@example.com"
    )

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if create:
            self.set_password(
                extracted or "Strong-Test-Password-123!"
            )
            self.save(update_fields=["password"])


class FinancialAccountFactory(
    factory.django.DjangoModelFactory
):
    class Meta:
        model = FinancialAccount

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(
        lambda n: f"Account {n}"
    )
    account_type = FinancialAccount.AccountType.BANK
    balance = "1000.00"
    currency = "INR"