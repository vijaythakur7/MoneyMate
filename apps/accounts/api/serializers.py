from rest_framework import serializers

from apps.accounts.models import FinancialAccount


class FinancialAccountSerializer(serializers.ModelSerializer):
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

        def validate_name(self, value):
            if not value.strip():
                raise serializers.ValidationError(
                "Account name cannot be empty."
            )

            return value