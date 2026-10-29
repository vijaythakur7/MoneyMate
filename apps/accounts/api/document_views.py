from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.accounts.api.document_serializers import (
    FinancialDocumentSerializer,
)
from apps.accounts.models import FinancialDocument

from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
class FinancialDocumentViewSet(ModelViewSet):
    serializer_class = FinancialDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return FinancialDocument.objects.filter(
            user=self.request.user
        ).order_by("-uploaded_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DocumentViewSet(ModelViewSet):
    serializer_class = FinancialDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FinancialDocument.objects.filter(
            user=self.request.user
        ).order_by("-uploaded_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=["get"],
        url_path="preview",
    )
    def preview(self, request, pk=None):
        document = self.get_object()

        if not document.file:
            raise ValidationError({"file": "No file is attached."})

        if not document.file.name.lower().endswith(".pdf"):
            raise ValidationError({"file": "Only PDF files are supported."})

        response = FileResponse(
            document.file.open("rb"),
            content_type="application/pdf",
        )
        response["Content-Disposition"] = 'inline; filename="document.pdf"'
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = "private, no-store"

        return response