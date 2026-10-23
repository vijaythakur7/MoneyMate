from django.urls import path

from apps.accounts.api.views import (
    # FinancialAccountListAPIView,
    FinancialAccountDetailAPIView,
    FinancialAccountListCreateAPIView,
)


urlpatterns = [
    path("accounts/",
        FinancialAccountListCreateAPIView.as_view(),
        name="api-account-list",
    ),
    path(
        "accounts/<int:account_id>/",
        FinancialAccountDetailAPIView.as_view(),
        name="api-account-detail",
    ),
]