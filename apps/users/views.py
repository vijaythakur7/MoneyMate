from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def hello(request):
    print("Method:", request.method)
    print("Path:", request.path)
    return HttpResponse("Hello from MoneyMate!")

def user_detail(request, id):
    return HttpResponse(f"User ID: {id}")

def search(request):
    query = request.GET.get("q")

    return HttpResponse(f"Search query: {query}")

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def login_view(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return JsonResponse(
            {"detail": "Invalid username or password."},
            status=401,
        )

    login(request, user)

    return JsonResponse(
        {"detail": "Login successful."},
        status=200,
    )

@require_POST
def logout_view(request):
    logout(request)

    return JsonResponse(
        {"detail": "Logout successful."},
        status=200,
    )