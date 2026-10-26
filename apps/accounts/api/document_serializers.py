from pathlib import Path

from rest_framework import serializers

from apps.accounts.models import FinancialDocument


class FinancialDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialDocument
        fields = (
            "id",
            "title",
            "file",
            "uploaded_at",
        )
        read_only_fields = ("id", "uploaded_at")

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Document title cannot be empty."
            )

        return value

    def validate_file(self, value):
        max_size = 5 * 1024 * 1024  # 5 MB

        if value.size > max_size:
            raise serializers.ValidationError(
                "File size must not exceed 5 MB."
            )

        if Path(value.name).suffix.lower() != ".pdf":
            raise serializers.ValidationError(
                "Only PDF files are allowed."
            )

        file_start = value.read(5)
        value.seek(0)

        if file_start != b"%PDF-":
            raise serializers.ValidationError(
                "The uploaded file is not a valid PDF file."
            )

        return value