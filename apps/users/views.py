from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def hello(request):
    print("Method:", request.method)
    print("Path:", request.path)
    return HttpResponse("Hello from MoneyMate!")