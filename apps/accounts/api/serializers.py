from rest_framework import serializers

from apps.accounts.models import FinancialAccount


class FinancialAccountSerializer(serializers.ModelSerializer):

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Account name cannot be empty."
            )

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            exists = FinancialAccount.objects.filter(
                user=request.user,
                name=value,
            ).exists()

            if exists:
                raise serializers.ValidationError(
                    "An account with this name already exists."
                )

        return value

    class Meta:
        model = FinancialAccount
        fields = (
            "id",
            "name",
            "account_type",
            "balance",
            "currency",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )