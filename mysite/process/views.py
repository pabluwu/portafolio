from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hola mundo")

def proyecto(request):
    return render(request, 'process/project.html')

# Create your views here.
