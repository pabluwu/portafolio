from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User, Group, Permission
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
from . import forms
from . import models
from . import filters

@login_required()
def index(request):
    return render(request, 'process/project.html')


def proyecto(request):
    return render(request, 'process/project.html')

## Gestión de tareas
@login_required()
def agregar_tarea(request):
    if request.user.has_perm('process.add_tarea'):
        calculoEstado = models.CalculoEstado()
        tarea = models.Tarea()
        semaforo = models.Semaforo()
        data= {
            'form': forms.TareaForm()
        }
        if request.method=='POST':
            formulario = forms.TareaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                formulario.save()
                tarea = formulario.save()
            
                
                calculoEstado.fechaActualCalculo = datetime.now()
                calculoEstado.tarea = tarea
                calculoEstado.save()

                semaforo.calculoEstado = calculoEstado
                semaforo.semaforoRojo = timedelta(days=7)
                semaforo.save()

                data["mensaje"] = "Guardado correctamente."
            else:
                data["form"] = formulario
        return render(request, 'process/tarea/agregar_tarea.html', data)
    else:
        return render(request,'process/error_permiso.html')


@login_required()
def listar_tareas(request):
    usuario = get_user_model()
    usuarios = usuario.objects.all()
    grupos = Group.objects.all()
    respuesta = models.RespuestaRechazo()
    rechazos = []
    calculos = []
    semaforos = []
    myFilter = None
    tareas = models.Tarea.objects.filter(realizado=False)
    for t in tareas:
        calculoEstado = models.CalculoEstado.objects.get(tarea=t)
        calculoEstado.fechaActualCalculo = datetime.now().date()
        calculoEstado.diasRestantes = t.fechaLimite - calculoEstado.fechaActualCalculo
        calculoEstado.save()
        calculos.append(calculoEstado)
        semaforo = models.Semaforo.objects.get(calculoEstado=calculoEstado)
        if calculoEstado.diasRestantes > semaforo.semaforoRojo:
            semaforo.estadoSemaforo = 'v'
        elif calculoEstado.diasRestantes < semaforo.semaforoRojo and calculoEstado.diasRestantes > timedelta(days=0):
            semaforo.estadoSemaforo = 'a'            
        elif calculoEstado.diasRestantes < timedelta(days=0):
            semaforo.estadoSemaforo = 'r'
        semaforo.save()
        semaforos.append(semaforo)


    if request.user.is_superuser:
        user = "all"
        tareas = models.Tarea.objects.filter(realizado=False)
        myFilter = filters.TareaFilter(request.GET, queryset=tareas)
        tareas = myFilter.qs
        if request.POST.get('filtroSemaforo'):
            tareas = filtroSemaforo(request.POST['filtroEstadoSemaforo'],user)
        elif request.POST.get('filtroUsuario'):
            tareas = models.Tarea.objects.filter(realizado=False, usuario=request.POST['filtro_usuario'])
        elif request.POST.get('limpiarFiltro'):
            tareas = models.Tarea.objects.filter(realizado=False)
        elif request.POST.get('filtroGrupo'):
            usuario_flag = usuario.objects.get(groups=request.POST['filtro_grupo'])
            tareas = models.Tarea.objects.filter(realizado=False, usuario=usuario_flag)
        else:
            tareas = models.Tarea.objects.filter(realizado=False)
    else:
        user = request.user
        tareas = models.Tarea.objects.filter(usuario = user, realizado = False)                                        
        #Bloque filtro por semáforo.
        if request.POST.get('filtroSemaforo'):
            tareas = filtroSemaforo(request.POST['filtroEstadoSemaforo'], user)
        else:
            tareas = models.Tarea.objects.filter(usuario = user, realizado = False)                                        
        
    

        
    data = {
        'tareas':tareas ,
        'semaforos':semaforos,
        'calculos':calculos,
        'filtro':myFilter,
        'usuarios':usuarios,
        'grupos':grupos,
    }
    return render(request, 'process/tarea/listar_tarea.html', data)

##Funciona que retorna las tareas en base al filtro del semáforo.
def filtroSemaforo(estado, user):
    tarea1 = models.Tarea()
    semaforos1 = models.Semaforo.objects.filter(estadoSemaforo=estado)
    calculo2 = []
    tareas = []
    for s in semaforos1:
        calculo1 = models.CalculoEstado.objects.get(id=s.calculoEstado.id)
        calculo2.append(calculo1)
    for c in calculo2:
            if user == 'all':
                try:
                    tarea1 = models.Tarea.objects.get(id=c.tarea.id, realizado=False)
                    tareas.append(tarea1)
                except tarea1.DoesNotExist:
                    tarea1 = None
            else:
                try:
                    tarea1 = models.Tarea.objects.get(id=c.tarea.id, realizado=False,usuario=user)
                    tareas.append(tarea1)
                except tarea1.DoesNotExist:
                    tarea1 = None
            
    return tareas

@login_required()
def listar_tareas_completadas(request):
    if request.user.is_superuser:
        tareas = models.Tarea.objects.filter(realizado = True)
    else:
        user = request.user
        tareas = models.Tarea.objects.filter(usuario = user, realizado = True)                                        

    data = {
        'tareas':tareas
    }
    return render(request, 'process/tarea/listar_tarea_completada.html', data)

@login_required()
def tarea_completada(request, id):
    tarea = get_object_or_404(models.Tarea, id=id)

    data={
        'form': forms.TareaCompletaForm(instance=tarea)
    }

    if request.method == 'POST':
        return redirect(to="listar_tareas_completadas")

    return render(request,'process/tarea/ver_tarea.html', data)

@login_required()
def modificar_tarea(request, id):
    rechazo = models.MotivoRechazo()
    respuestaRechazo = models.RespuestaRechazo()
    tarea = get_object_or_404(models.Tarea, id=id)
    data_form = forms.SolicitudRechazoForm()

    ##Código para actualizar semáforo.
    calculoEstado = models.CalculoEstado.objects.get(tarea=tarea)
    semaforo = models.Semaforo.objects.get(calculoEstado=calculoEstado)

    ##Códido para obtener si hay o no solicitudes de rechazo para esta tarea, y en
    ##caso de haber, si tuvo la respuesta.
    try:
        rechazo = models.MotivoRechazo.objects.get(tarea=tarea, respondido=False)
        data_form={'descripcion':rechazo.descripcion,
        'usuario':rechazo.usuario.get_short_name(),
        'tarea':rechazo.tarea.nombre}
    except rechazo.DoesNotExist: 
        rechazo = None
    try:
        respuestaRechazo = models.RespuestaRechazo.objects.get(motivoRechazo=rechazo)
    except respuestaRechazo.DoesNotExist:
        respuestaRechazo = None

    forms 

    print(rechazo)
    print(respuestaRechazo)
    data={
        'form': forms.TareaForm(instance=tarea),
        'formRechazo': forms.RechazoForm(),
        'formSolicitudRechazo': forms.SolicitudRechazoForm(data_form),
        'formRespuesta': forms.RespuestaSolicitudForm(),
        'formRespuestaSolicitud': forms.RespuestaSolicitudRespondidaForm(instance=respuestaRechazo),
        'rechazo': rechazo,
        'respuestaRechazo': respuestaRechazo,
        'tarea': tarea,
        'calculoEstado':calculoEstado,
        'semaforo':semaforo
    }

    if request.method == 'POST':
        if request.POST.get("form_type") == 'modificarform':
            formulario = forms.TareaForm(data=request.POST, instance=tarea, files=request.FILES)
            if formulario.is_valid():
                if request.POST.get('terminar'):
                    tarea.realizado = True
                    tarea.fechaTermino = datetime.now()
                    tarea.save()
                    return HttpResponseRedirect('/listar/tarea')
                else:    
                    formulario.save()
                    return redirect(to="listar_tareas")
            data["form"] = formulario

        if request.POST.get("form_type") == 'motivoform':
            if  rechazo == None and tarea.usuario != None:
                formularioRechazo = forms.RechazoForm(data=request.POST, files=request.FILES)
                motivoRechazo = models.MotivoRechazo()
                if formularioRechazo.is_valid():
                    motivoRechazo.descripcion=formularioRechazo['descripcion'].value()
                    motivoRechazo.usuario=request.user
                    motivoRechazo.tarea=tarea
                    motivoRechazo.save()
                    tarea.usuario=None
                    tarea.save()
                    return redirect(to="listar_tareas")
            # elif rechazo != None:
        if request.POST.get("problema") == 'reportar_problema':
            print("problemaaaaa")
            request.session['id_tarea'] = tarea.id
            return redirect(to="reportar_problema")
            


                
                
        if request.POST.get("form_type") == 'solicitudform':
            formRespustaRechazo = forms.RespuestaSolicitudForm(data=request.POST, files=request.FILES)
            respuestaRechazo = models.RespuestaRechazo()
            if formRespustaRechazo.is_valid():
                respuestaRechazo.respuesta=formRespustaRechazo['respuesta'].value()
                if request.POST.get('rechazarSolicitud'):
                    respuestaRechazo.aceptado=False
                    tarea.usuario = rechazo.usuario
                    tarea.save()
                elif request.POST.get('aceptarSolicitud'):
                    respuestaRechazo.aceptado=True
                    tarea.usuario = None
                    tarea.save()
                respuestaRechazo.motivoRechazo = rechazo
                respuestaRechazo.save()
                rechazo.respondido = True
                rechazo.save()
                return redirect(to="listar_tareas")
                
   


    return render(request,'process/tarea/modificar_tarea.html', data)

## Gestión flujo de tareas

@login_required()
def agregar_flujo_tarea(request):
    if request.user.has_perm('process.add_flujotarea'):
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
    if request.user.has_perm('process.change_flujotarea'):
        flujo_tareas = models.FlujoTarea.objects.all()
        data = {
            'flujo_tareas':flujo_tareas
        }
        return render(request, 'process/flujo_tarea/listar_flujo_tareas.html', data)
    else:
        return render(request,'process/error_permiso.html')

@login_required()
def modificar_flujo_tarea(request, id):
    if request.user.has_perm('process.change_flujotarea'):
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
                if len(password1) > 7:
                    if password1 == password2:
                        if formulario.is_valid():
                            formulario.save()
                            data["mensaje"] = "Guardado correctamente."
                            print("guardado")
                        else:
                            data["mensaje"] = "Contraseña insegura."
                            data["form"] = formulario
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
        'email':usuario.email,
        'grupos':usuario.groups.all()}
        data={
            'form': forms.UsuarioFormulario(data_form)
        }
        if request.method=='POST':
            formulario = forms.UsuarioFormulario(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                usuario.groups.clear()
                for i in formulario['grupos'].value():
                    grupos, created = Group.objects.get_or_create(id=i)
                    usuario.groups.add(grupos)
                usuario.first_name=formulario['nombre'].value()
                usuario.last_name=formulario['apellido'].value()
                usuario.email=formulario['email'].value()
                usuario.save()
                data["mensaje"] = "Modificado correctamente."
                data["form"] = formulario

        return render(request,'registration/modificar_usuario.html', data)
    else:
        return render(request,'process/error_permiso.html')


##Gestión de grupos y roles.
@login_required()
def agregar_grupo(request):
    if request.user.is_superuser:
        data={
            'form': forms.GroupForm()
        }
        if request.method=='POST':
            formulario = forms.GroupForm(data=request.POST)
            nombre = formulario['nombre'].value()
            permisos = formulario['permisos'].value()
            permiso = Permission.objects.all()
            grupo_nuevo, created = Group.objects.get_or_create(name=nombre)
            for i in permisos:
                permiso = Permission.objects.get(codename=i)
                grupo_nuevo.permissions.add(permiso)
                print(i)
            grupo_nuevo.save()
        return render(request,'process/grupos_roles/agregar_grupo.html', data)
    else:
        return render(request,'process/error_permiso.html')

##Gestión problemas y errores.
@login_required()
def reportar_problema(request):

    id_tarea = request.session.get('id_tarea')
    tarea = get_object_or_404(models.Tarea, id=id_tarea)
    reportar_problema = models.ReportarProblema()
    data = {
        'form': forms.ReportarProblemaForm(),
        'tarea': tarea,
    }
    if request.method=='POST':
            formulario = forms.ReportarProblemaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                reportar_problema.descripcion = formulario['descripcion'].value()
                reportar_problema.tarea = tarea
                reportar_problema.save()    

                data["mensaje"] = "Guardado correctamente."

            else:
                data["form"] = formulario
    return render(request,'process/problemas/registrar_problema.html', data)

def listar_problemas(request):
    if request.user.has_perm('process.add_respuestaproblema'):
        reportes = models.ReportarProblema.objects.all()
        for r in reportes:
            print(r.tarea.usuario.email)
        tareas = models.Tarea.objects.all()
        data = {
        'reportes': reportes,
        }   
        return render(request, 'process/problemas/listar_problemas.html', data)
    else:
        return render(request,'process/error_permiso.html')

def responder_problema(request, id):
    if request.user.has_perm('process.add_respuestaproblema'):
        reporte = models.ReportarProblema.objects.get(id=id)
        try:
            respuesta = models.RespuestaProblema.objects.get(problema=reporte)
        except:
            respuesta = models.RespuestaProblema()

        data={
            'reporte': reporte,
            'form': forms.RevisarReporteForm(instance=reporte),
            'formSolucion': forms.SolucionProblemaForm(),
        }
        if reporte.estado == False:
            if request.method=='POST':
                    formulario = forms.SolucionProblemaForm(data=request.POST, files=request.FILES)
                    if formulario.is_valid():
                        respuesta.respuesta = formulario['respuesta'].value()
                        respuesta.problema = reporte
                        reporte.estado = True
                        reporte.save()
                        respuesta.save()    

                        data["mensaje"] = "Guardado correctamente."

                    else:
                        data["form"] = formulario
        else:
            data["formSolucion"] = forms.SolucionProblemaOkForm(instance=respuesta)
            print(respuesta.respuesta)
        return render(request, 'process/problemas/responder_problema.html', data)
    else:
        return render(request,'process/error_permiso.html')

