from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from . import forms
from . import models

@login_required()
def index(request):
    return render(request, 'process/project.html')


def proyecto(request):
    return render(request, 'process/project.html')

## Gestión de tareas
@login_required()
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
    return render(request, 'process/tarea/agregar_tarea.html', data)

@login_required()
def listar_tareas(request):
    tareas = models.Tarea.objects.all()
    data = {
        'tareas':tareas
    }
    return render(request, 'process/tarea/listar_tarea.html', data)

@login_required()
def modificar_tarea(request, id):
    tarea = get_object_or_404(models.Tarea, id=id)

    data={
        'form': forms.TareaForm(instance=tarea)
    }

    if request.method == 'POST':
        formulario = forms.TareaForm(data=request.POST, instance=tarea, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listar_tareas")
        data["form"] = formulario
    return render(request,'process/tarea/modificar_tarea.html', data)

## Gestión flujo de tareas

@login_required()
def agregar_flujo_tarea(request):
    if request.user.is_superuser:
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
        
        return render(request, 'process/flujo_tarea/agregar_flujo_tarea.html', data)
    else:
        return render(request,'process/error_permiso.html')

@login_required()
def listar_flujo_tareas(request):
    if request.user.is_superuser:
        flujo_tareas = models.FlujoTarea.objects.all()
        data = {
            'flujo_tareas':flujo_tareas
        }
        return render(request, 'process/flujo_tarea/listar_flujo_tareas.html', data)
    else:
        return render(request,'process/error_permiso.html')

@login_required()
def modificar_flujo_tarea(request, id):
    if request.user.is_superuser:
        flujo_tarea = get_object_or_404(models.FlujoTarea, id=id)

        data={
            'form': forms.FlujoTareaForm(instance=flujo_tarea)
        }

        if request.method == 'POST':
            formulario = forms.FlujoTareaForm(data=request.POST, instance=flujo_tarea, files=request.FILES)
            if formulario.is_valid():
                formulario.save()
                return redirect(to="listar_flujo_tareas")
            data["form"] = formulario
        return render(request,'process/flujo_tarea/modificar_flujo_tarea.html', data)
    else:
        return render(request,'process/error_permiso.html')

##Gestión de usuarios.
@login_required()
def registrar_usuario(request):
    if request.user.is_superuser:
        data={
            'form': forms.UserCreationForm()
        }

        if request.method=='POST':
            formulario = forms.UserCreationForm(data=request.POST)
            print("formulario")
            username = formulario['username'].value()
            password1 = formulario['password1'].value()
            password2 = formulario['password2'].value()
            if len(username) >= 5:
                print(username)
                if len(password1) > 7:
                    if password1 == password2:
                        if formulario.is_valid():
                            formulario.save()
                            data["mensaje"] = "Guardado correctamente."
                            print("guardado")
                    else:
                        data["mensaje"] = "Contraseñas no coinciden"
                        data["form"] = formulario
                else:
                    data["mensaje"] = "Contraseña demasiado corta"
                    data["form"] = formulario
            else:
                data["mensaje"] = "Nombre de usuario debe ser mayor a 5 caracteres."
                data["form"] = formulario
        return render(request,'registration/register_user.html', data) 
    else:
        return render(request,'process/error_permiso.html')

@login_required()
def listar_usuarios(request):
    if request.user.is_superuser:
        User = get_user_model()
        users = User.objects.all()
        data={
            'users':users 
        }
        return render(request, 'registration/listar_usuarios.html', data)
    else:
        return render(request,'process/error_permiso.html')

@login_required()
def modificar_usuario_admin(request, id):
    if request.user.is_superuser:
        User = get_user_model()
        usuario = get_object_or_404(User, id=id)
        data_form={'username':usuario.get_username(),
        'nombre':usuario.get_short_name(),
        'apellido':usuario.last_name,
        'email':usuario.email}
        print(usuario)
        data={
            'form': forms.UsuarioFormulario(data_form)
        }
        if request.method=='POST':
            formulario = forms.UsuarioFormulario(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                usuario.first_name=formulario['nombre'].value()
                usuario.last_name=formulario['apellido'].value()
                usuario.email=formulario['email'].value()
                usuario.save()
                data["mensaje"] = "Modificado correctamente."

        return render(request,'registration/modificar_usuario.html', data)
    else:
        return render(request,'process/error_permiso.html')


##Gestión de grupos y roles POR HACER.
@login_required()
def agregar_grupo(request):
    if request.user.is_superuser:
        data={
            'form': forms.GroupForm()
        }
        return render(request,'process/grupos_roles/agregar_grupo.html', data)
    else:
        return render(request,'process/error_permiso.html')


# Create your views here.
