
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    password_confirm = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "mobile_number",
            "currency",
            "timezone",
        )
        read_only_fields = ("id",)

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate_username(self, value):
        value = value.strip()

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })

        return attrs
