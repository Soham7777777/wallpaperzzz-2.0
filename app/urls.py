from django.urls import path
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def view_function(request: HttpRequest) -> HttpResponse:
    return render(request, 'base.html')


urlpatterns = [
    path('', view_function)
]
