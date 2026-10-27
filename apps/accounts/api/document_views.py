from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.accounts.api.document_serializers import (
    FinancialDocumentSerializer,
)
from apps.accounts.models import FinancialDocument


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