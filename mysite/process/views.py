from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from . import forms

def index(request):
    return render(request, 'registration/login.html')

def proyecto(request):
    return render(request, 'process/project.html')

def agregar_flujo_tarea(request):
    data = {
        'form': forms.FlujoTareaForm()
    }
    if request.method == 'POST':
        formulario = forms.FlujoTareaForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            data["mensaje"] = "Guardado correctamente."
        else:
            data["form"] = formulario
    
    return render(request, 'process/agregar_flujo_tarea.html', data)


def agregar_tarea(request):
    data= {
        'form': forms.TareaForm()
    }
    if request.method=='POST':
        formulario = forms.TareaForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            data["mensaje"] = "Guardado correctamente."
        else:
            data["form"] = formulario
    return render(request, 'process/agregar_tarea.html', data)



# Create your views here.
