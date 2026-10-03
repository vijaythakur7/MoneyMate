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