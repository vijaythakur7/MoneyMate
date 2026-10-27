
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import FinancialDocument

User = get_user_model()


class FinancialDocumentUploadTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="documentuser",
            email="document@example.com",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)
        self.url = "/api/documents/"

    def test_user_can_upload_pdf(self):
        pdf = SimpleUploadedFile(
            "statement.pdf",
            b"%PDF-1.4\nSample PDF content",
            content_type="application/pdf",
        )

        response = self.client.post(
            self.url,
            {
                "title": "Bank Statement",
                "file": pdf,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        document = FinancialDocument.objects.get(
            user=self.user,
            title="Bank Statement",
        )

        self.assertTrue(document.file.name.endswith(".pdf"))

    def test_non_pdf_file_is_rejected(self):
        file = SimpleUploadedFile(
            "notes.txt",
            b"Not a PDF",
            content_type="text/plain",
        )

        response = self.client.post(
            self.url,
            {
                "title": "Notes",
                "file": file,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            FinancialDocument.objects.filter(
                user=self.user,
                title="Notes",
            ).exists()
        )

    def test_user_cannot_retrieve_another_users_document(self):
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="TestPassword123!",
        )

        document = FinancialDocument.objects.create(
            user=other_user,
            title="Private Statement",
            file=SimpleUploadedFile(
                "private.pdf",
                b"%PDF-1.4\nSample PDF content",
                content_type="application/pdf",
            ),
        )

        response = self.client.get(
            f"{self.url}{document.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )