from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import FinancialAccount


@login_required
def financial_account_list(request):
    accounts = FinancialAccount.objects.filter(
        user=request.user,
    )

    data = [
        {
            "id": account.id,
            "name": account.name,
            "account_type": account.account_type,
            "balance": str(account.balance),
            "currency": account.currency,
        }
        for account in accounts
    ]

    return JsonResponse(
        {
            "accounts": data,
        }
    )

@login_required
def financial_account_detail(request, account_id):
    account = get_object_or_404(
        FinancialAccount,
        id=account_id,
        user=request.user,
    )

    if request.method == "GET":
        return JsonResponse({
            "id": account.id,
            "name": account.name,
            "account_type": account.account_type,
            "balance": str(account.balance),
            "currency": account.currency,
        })

    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            return JsonResponse(
                {"detail": "Name is required."},
                status=400,
            )
        account.name = name
        account.save()

        return JsonResponse({
            "id": account.id,
            "name": account.name,
        })

    if request.method == "DELETE":
        account.delete()

        return JsonResponse(
        {"detail": "Account deleted successfully."},
        status=200,
    )

    return JsonResponse(
        {"detail": "Method not allowed."},
        status=405,
    )