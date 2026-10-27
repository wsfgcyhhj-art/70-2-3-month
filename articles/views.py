from django.shortcuts import render
from django.http.response import HttpResponse


def hello_world(request):
    return HttpResponse("<h1>Hello world!</h1>")


def hello_name(request, name):
    return HttpResponse(f"Hello <h1>{name}</h1>!")


def about(request):
    return HttpResponse("<h1>О проекте</h1><p>Учебный блог на Django.</p>")
