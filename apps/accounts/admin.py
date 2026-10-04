from django.contrib import admin

# Register your models here.

from .models import FinancialAccount


@admin.register(FinancialAccount)
class FinancialAccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "account_type",
        "balance",
        "currency",
        "created_at",
    )

    list_filter = (
        "account_type",
        "currency",
    )

    search_fields = (
        "name",
        "user__username",
        "user__email",
    )