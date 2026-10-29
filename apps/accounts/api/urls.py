from django.urls import path

# from apps.accounts.api.views import (
#     # FinancialAccountListAPIView,
#     FinancialAccountDetailAPIView,
#     FinancialAccountListCreateAPIView,
# )
# urlpatterns = [
#     path("accounts/",
#         FinancialAccountListCreateAPIView.as_view(),
#         name="api-account-list",
#     ),
#     path(
#         "accounts/<int:account_id>/",
#         FinancialAccountDetailAPIView.as_view(),
#         name="api-account-detail",
#     ),
# ]
from rest_framework.routers import DefaultRouter

from apps.accounts.api.document_views import (
    FinancialDocumentViewSet,DocumentViewSet
)
from apps.accounts.api.views import (
    FinancialAccountViewSet,
    GenerateMonthlyReportAPIView,
)

router = DefaultRouter()

router.register(
    "accounts",
    FinancialAccountViewSet,
    basename="api-account",
)

router.register(
    "documents",
    DocumentViewSet,
    basename="document",
)

urlpatterns = [
    path(
        "reports/monthly/",
        GenerateMonthlyReportAPIView.as_view(),
        name="monthly-report",
    ),
    *router.urls,
]