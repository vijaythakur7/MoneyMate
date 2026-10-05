from django.urls import path

from apps.accounts.api.views import FinancialAccountListAPIView


urlpatterns = [
    path("accounts/",FinancialAccountListAPIView.as_view(),name="api-account-list",),
]