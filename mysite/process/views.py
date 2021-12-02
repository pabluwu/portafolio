from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User, Group, Permission
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime, timedelta
from django.db import connection
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
                

                if formulario['is_tipo'].value() == True:
                    usuario = get_object_or_404(models.User,id=formulario['usuario'].value())
                    # print(usuario)
                    # print(formulario['fechaLimite'].value())
                    date = datetime.strptime(formulario['fechaLimite'].value(),'%m/%d/%Y')
                    tarea = models.Tarea(
                        nombre=formulario['nombre'].value(),
                        descripcion=formulario['descripcion'].value()+" / Tarea tipo /",
                        is_tipo=True,
                        fechaCreacion=datetime.now(),
                        fechaLimite=date,
                        usuario=usuario,
                    )
                    tarea.save()
                else:
                    formulario.save()
                    tarea = formulario.save()
                
                    
                    calculoEstado.fechaActualCalculo = datetime.now()
                    calculoEstado.tarea = tarea
                    calculoEstado.save()

                    semaforo.calculoEstado = calculoEstado
                    semaforo.semaforoRojo = timedelta(days=7)
                    semaforo.save() 

                messages.success(request, "Tarea guardada correctamente")
                data["form"] = formulario
            else:
                formulario = forms.TareaForm()
                data["form"] = formulario
        return render(request, 'process/tarea/agregar_tarea.html', data)
    else:
        return render(request,'process/error_permiso.html')

def actualizar_semaforo():
    tareas = models.Tarea.objects.filter(realizado=False, is_tipo=False)    
    for t in tareas:
        calculoEstado = models.CalculoEstado.objects.get(tarea=t)
        calculoEstado.fechaActualCalculo = datetime.now().date()
        calculoEstado.diasRestantes = t.fechaLimite - calculoEstado.fechaActualCalculo
        calculoEstado.save()
        semaforo = models.Semaforo.objects.get(calculoEstado=calculoEstado)
        if calculoEstado.diasRestantes > semaforo.semaforoRojo:
            semaforo.estadoSemaforo = 'v'
        elif calculoEstado.diasRestantes < semaforo.semaforoRojo and calculoEstado.diasRestantes > timedelta(days=0):
            semaforo.estadoSemaforo = 'a'            
        elif calculoEstado.diasRestantes <= timedelta(days=0):
            semaforo.estadoSemaforo = 'r'
        semaforo.save()


@login_required()
def listar_tareas(request):
    usuario = get_user_model()
    usuarios = usuario.objects.all()
    departamento_combo = models.Departamento.objects.all()
    respuesta = models.RespuestaRechazo()
    rechazos = []
    calculos = []
    semaforos = []
    myFilter = None
    tareas = models.Tarea.objects.filter(realizado=False, is_tipo=False)    
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
        elif calculoEstado.diasRestantes <= timedelta(days=0):
            semaforo.estadoSemaforo = 'r'
        semaforo.save()
        semaforos.append(semaforo)
        


    if request.user.is_superuser:
        user = "all"
        tareas = models.Tarea.objects.filter(realizado=False,is_tipo=False)
        myFilter = filters.TareaFilter(request.GET, queryset=tareas)
        tareas = myFilter.qs
        if request.POST.get('filtroSemaforo'):
            tareas = filtroSemaforo(request.POST['filtroEstadoSemaforo'],user)
        elif request.POST.get('filtroUsuario'):
            tareas = models.Tarea.objects.filter(realizado=False, usuario=request.POST['filtro_usuario'],is_tipo=False)
        elif request.POST.get('limpiarFiltro'):
            tareas = models.Tarea.objects.filter(realizado=False,is_tipo=False)
        elif request.POST.get('filtroGrupo'):
            departamento = get_object_or_404(models.Departamento, id=request.POST['filtro_grupo'])
            tareas_departamento = listar_tareas_departamento(departamento.id,0)
            tareas = []
            for t in tareas_departamento:
                tarea1 = models.Tarea.objects.get(id=t[0])
                tareas.append(tarea1) 
            # tareas = models.Tarea.objects.filter(realizado=False, usuario=usuario_flag)
        else:
            tareas = models.Tarea.objects.filter(realizado=False,is_tipo=False)
    else:
        user = request.user
        tareas = models.Tarea.objects.filter(usuario = user, realizado = False, is_tipo=False)                                        
        #Bloque filtro por semáforo.
        if request.POST.get('filtroSemaforo'):
            tareas = filtroSemaforo(request.POST['filtroEstadoSemaforo'], user)
        else:
            tareas = models.Tarea.objects.filter(usuario = user, realizado = False,is_tipo=False)                                        
        
        
    data = {
        'tareas':tareas ,
        'semaforos':semaforos,
        'calculos':calculos,
        'filtro':myFilter,
        'usuarios':usuarios,
        'departamento_combo':departamento_combo,
    }
    return render(request, 'process/tarea/listar_tarea.html', data)

@login_required()
def listar_rechazos_tarea(request):
    tareas_rechazadas = []
    t = []
    if request.user.has_perm('process._add_respuestarechazo'):
        tareas_rechazadas = listar_tareas_rechazadas(0)
        if request.POST.get('solicitudes_no_respondidas'):
            tareas_rechazadas = listar_tareas_rechazadas(0)
        elif request.POST.get('solicitudes_respondidas'):
            tareas_rechazadas = listar_tareas_rechazadas(1)
    else: 
        user = request.user
        if request.POST.get('solicitudes_no_respondidas'):
            tareas = listar_tareas_rechazadas(0)
            for t in tareas:
                if t[3] == user.id:
                    tareas_rechazadas.append(t)
        elif request.POST.get('solicitudes_respondidas'):
            tareas = listar_tareas_rechazadas(1)
            for t in tareas:
                if t[3] == user.id:
                    tareas_rechazadas.append(t)
                
    data = {
        'tareas_rechazadas':tareas_rechazadas ,
        
    }
    return render(request, 'process/tarea/listar_rechazos_tarea.html', data)

@login_required
def revisar_rechazo_tarea(request, id, id_rechazo):
    rechazo = models.MotivoRechazo()
    respuestaRechazo = models.RespuestaRechazo()
    tarea = get_object_or_404(models.Tarea, id=id)
    data_form = {}
    try:
        rechazo = models.MotivoRechazo.objects.get(id=id_rechazo)
        data_form={'descripcion':rechazo.descripcion,
            'usuario':rechazo.usuario.username,
            'tarea':rechazo.tarea.nombre}
    except:
        rechazo = None
    data_form_tarea = forms.TareaRechazoForm()
    data_form_tarea={
        'nombre':tarea.nombre,
        'descripcion':tarea.descripcion,
        'fecha_limite':tarea.fechaLimite,
        'usuario_rechazo':'pepito',
    }
        
    try:
        respuestaRechazo = models.RespuestaRechazo.objects.get(motivoRechazo=rechazo)
    except respuestaRechazo.DoesNotExist:
        respuestaRechazo = None
        print('no hay respuesta')

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
            return redirect(to="listar_rechazos_tarea")
                
    data = {
        'form': forms.TareaRechazoForm(data_form_tarea),
        'formRechazo': forms.RechazoForm(),
        'formSolicitudRechazo': forms.SolicitudRechazoForm(data_form),
        'formRespuesta': forms.RespuestaSolicitudForm(),
        'formRespuestaSolicitud': forms.RespuestaSolicitudRespondidaForm(instance=respuestaRechazo),
        'rechazo': rechazo,
        'respuestaRechazo': respuestaRechazo,
    }
    return render(request, 'process/tarea/revisar_rechazo_tarea.html', data)

#Procedimiento pl/sql tareas rechazadas.
def listar_tareas_rechazadas(rechazo_respondido):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_TAREAS_RECHAZADAS',[rechazo_respondido,out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)
    
    return lista


##Funcion que retorna las tareas en base al filtro del semáforo.
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
        tareas = listar_tareas_bd(1,1,1)
    else:
        user = request.user
        tareas = listar_tareas_bd(1,0,user.id)

    data = {
        'tareas':tareas
    }
    return render(request, 'process/tarea/listar_tarea_completada.html', data)

@login_required()
def tarea_completada(request, id):
    data_form = forms.TareaCompletaForm()
    tarea = detalle_tarea_bd(id)
    tareas_subordinadas = models.Tarea()
    for t in tarea:
        data_form = {
            'nombre':t[1],
            'descripcion':t[2],
            'realizado':t[3],
            'fecha_limite':t[4],
            'fecha_termino':t[5],
            'usuario':t[7]
        }
    
    try:
        tareas_subordinadas = models.Tarea.objects.filter(tarea_parent=tarea[0][0])
    except:
        tareas_subordinadas = []    
    
    print(tareas_subordinadas)
    data = {
        'form':forms.TareaCompletaForm(data_form),
        'tareas_subordinadas':tareas_subordinadas,
    }

    if request.method == 'POST':
        return redirect(to="listar_tareas_completadas")

    return render(request,'process/tarea/ver_tarea.html', data)

def listar_tareas_bd(estado_tarea,is_superuser,usuario_id):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_TAREAS',[estado_tarea,is_superuser,usuario_id,out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)
    
    return lista

def detalle_tarea_bd(tarea_id):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_DETALLE_TAREA',[tarea_id,out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)
    
    return lista

@login_required()
def modificar_tarea(request, id):
    tarea = get_object_or_404(models.Tarea, id=id)
    user = request.user
    usuarios = []
    try:
        otra_tarea = models.Tarea.objects.filter(tarea_parent=tarea)
        for o in otra_tarea:
            print(o.usuario)
            usuarios.append(o.usuario)
            
        print(usuarios)
        print(user)
    except:
        pass

    
        print("Mismo usuario")
    else:
        print("usuario distinto")
    rechazo = models.MotivoRechazo()
    respuestaRechazo = models.RespuestaRechazo()
    
    if tarea.realizado is False:
        if tarea.usuario == user or user in usuarios:
            
            data_form = forms.SolicitudRechazoForm()
            tareas_subordinadas = models.Tarea()

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

            ##Código para listar tareas subordinadas en caso de haber\
            contar_tareas = []
            contar_tareas_subordinadas = []
            try:
                tareas_subordinadas = models.Tarea.objects.filter(tarea_parent=tarea).order_by('realizado')
                tareas_subordinadas_realizadas = models.Tarea.objects.filter(tarea_parent=tarea, realizado=True)
                tareas_subordinadas_no_realizadas = models.Tarea.objects.filter(tarea_parent=tarea, realizado=False)
                
                x = round((len(tareas_subordinadas_realizadas)*100)/len(tareas_subordinadas),2)
                print(x)
                contar_tareas_subordinadas.append(len(tareas_subordinadas))
                contar_tareas_subordinadas.append(len(tareas_subordinadas_realizadas))
                contar_tareas_subordinadas.append(len(tareas_subordinadas_no_realizadas))
                contar_tareas_subordinadas.append(x)
            except:
                contar_tareas_subordinadas.append(0)
                pass
                

            forms 
            data={
                'form': forms.TareaModificarForm(instance=tarea),
                'formRechazo': forms.RechazoForm(),
                'formTarea': forms.TareaSubordinadaForm(),
                'formSolicitudRechazo': forms.SolicitudRechazoForm(data_form),
                'formRespuesta': forms.RespuestaSolicitudForm(),
                'formRespuestaSolicitud': forms.RespuestaSolicitudRespondidaForm(instance=respuestaRechazo),
                'rechazo': rechazo,
                'respuestaRechazo': respuestaRechazo,
                'tarea': tarea,
                'calculoEstado':calculoEstado,
                'semaforo':semaforo,
                'tareas_subordinadas':tareas_subordinadas,
                'contar_tareas_subordinadas':contar_tareas_subordinadas,
                
            }

            if request.method == 'POST':
                if request.POST.get("form_type") == 'modificarform':
                    formulario = forms.TareaModificarForm(data=request.POST, instance=tarea, files=request.FILES)
                    if formulario.is_valid():
                        if request.POST.get('terminar'):
                            tarea.realizado = True
                            tarea.fechaTermino = datetime.now()
                            tarea.save()

                            ##Terminar tareas subordinadas en caso de tener.
                            try:
                                tareas_subordinadas = models.Tarea.objects.filter(tarea_parent=tarea)
                                for t in tareas_subordinadas:
                                    t.realizado = True
                                    t.save()
                            except:
                                pass

                            messages.success(request, "Tarea terminada correctamente")
                            return redirect(to="listar_tareas")
                        else:    
                            formulario.save()
                            messages.success(request, "Modificado correctamente")
                            return redirect(to="listar_tareas")
                            
                    data["form"] = formulario
                if request.POST.get("form_type") == 'agregar_tarea_subordinada':
                    formulario_tarea = forms.TareaSubordinadaForm(data=request.POST, files=request.FILES)
                    if formulario_tarea.is_valid():
                        nueva_tarea = formulario_tarea.save()
                        tarea = get_object_or_404(models.Tarea, id=id)
                        nueva_tarea.tarea_parent = tarea
                        nueva_tarea.save()
                        print(nueva_tarea.tarea_parent)

                        calculoEstado = models.CalculoEstado()
                        semaforo = models.Semaforo()
                        calculoEstado.fechaActualCalculo = datetime.now()
                        calculoEstado.tarea = nueva_tarea
                        calculoEstado.save()

                        semaforo.calculoEstado = calculoEstado
                        semaforo.semaforoRojo = timedelta(days=7)
                        semaforo.save() 
                        messages.success(request, "Tarea subordinada creada correctamente")
                        return redirect(to="modificar_tarea",id=tarea.id)
                
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
        else:
            return render(request,'process/error_permiso.html')
    else:
        return redirect(to="tarea_completada",id=tarea.id)
                
   


    

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
                flujo_tarea = models.FlujoTarea()
                flujo_tarea.nombre = formulario['nombre'].value()
                flujo_tarea.save()
                for i in formulario['tareas'].value():
                    tarea = get_object_or_404(models.Tarea, id=i)
                    flujo_tarea.tareas.add(tarea)
                flujo_tarea.save()
                messages.success(request, "Flujo añadido correctamente")
            else:
                formulario = forms.FlujoTareaForm()
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
        print(flujo_tarea.tareas.all())

        data={
            'form': forms.FlujoModificarForm(instance=flujo_tarea)
        }

        if request.method == 'POST':
            formulario = forms.FlujoModificarForm(data=request.POST, instance=flujo_tarea, files=request.FILES)
            if formulario.is_valid():
                if request.POST.get('editar'):
                    flujo_tarea.tareas.clear()
                    for i in formulario['tareas'].value():
                        print(i)
                        flujo_tarea.tareas.add(i)
                    formulario.save()
                    messages.success(request, "Flujo modificado correctamente")
                elif request.POST.get('ejecutar'):
                    flujo_tarea = get_object_or_404(models.FlujoTarea, id=id)
                    for p in flujo_tarea.tareas.all(): 
                        calculoEstado = models.CalculoEstado()
                        semaforo = models.Semaforo()
                        t = models.Tarea.objects.get(id=p.id)
                        
                        now = datetime.now()
                        fecha = now.strftime("%m/%d/%Y, %H:%M:%S")
                        date = datetime.strptime(formulario['fechaLimite'].value(),'%m/%d/%Y')
                        tarea_nueva = models.Tarea(
                            nombre = t.nombre+" / "+flujo_tarea.nombre,
                            descripcion = t.descripcion+" / "+flujo_tarea.nombre+" Ejecutada el: "+fecha,
                            realizado = False,
                            is_tipo = False,
                            fechaLimite = date,
                            usuario = t.usuario
                        )
                        tarea_nueva.save()
                        calculoEstado.fechaActualCalculo = datetime.now()
                        calculoEstado.tarea = tarea_nueva
                        calculoEstado.save()

                        semaforo.calculoEstado = calculoEstado
                        semaforo.semaforoRojo = timedelta(days=7)
                        semaforo.save()
                        print(p)
                        # print(t)
                        print(semaforo)
                        print(calculoEstado)
                        print(tarea_nueva)
                        
                        
                    messages.success(request, "Flujo ejecutado correctamente")

                
            data["form"] = formulario
        return render(request,'process/flujo_tarea/modificar_flujo_tarea.html', data)
    else:
        return render(request,'process/error_permiso.html')

# def obtener_tareas_flujo(id_flujo):

##Gestión de usuarios.
@login_required()
def registrar_usuario(request):
    if request.user.is_superuser:
        data={
            'form': forms.UserCreationForm()
        }

        if request.method=='POST':
            formulario = forms.UserCreationForm(data=request.POST)
            username = formulario['username'].value()
            password1 = formulario['password1'].value()
            password2 = formulario['password2'].value()
            if len(username) >= 5:
                if len(password1) > 7:
                    if password1 == password2:
                        if formulario.is_valid():
                            user = models.User.objects.get(username=formulario.save())
                            grupos = Group.objects.get(id=formulario['groups'].value())                            
                            user.groups.add(grupos)  
                            user.save()                         
                            formulario.save()
                            messages.success(request, "Usuario registrado correctamente")
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
    User = get_user_model()
    user_flag = request.user
    usuario = get_object_or_404(User, id=id)
    if request.user.is_superuser or user_flag == usuario :
        
        
        data_form={'username':usuario.get_username(),
        'nombre':usuario.get_short_name(),
        'apellido':usuario.last_name,
        'email':usuario.email,
        'grupos':usuario.groups.first(),
        'departamento':usuario.departamento}
        data={
            'form': forms.UsuarioFormulario(data_form),
            'user':usuario
        }
        if request.method=='POST':
            formulario = forms.UsuarioFormulario(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                usuario.groups.clear()
                grupos = Group.objects.get(id=formulario['grupos'].value())
                usuario.groups.add(grupos)
                # for i in formulario['grupos'].value():
                #     print(i)
                #     grupos = Group.objects.get(id=i)
                #     print(grupos)
                #     usuario.groups.add(grupos)
                #     grupos.user_set.add(usuario)
                usuario.first_name=formulario['nombre'].value()
                usuario.last_name=formulario['apellido'].value()
                usuario.email=formulario['email'].value()
                departamento = get_object_or_404(models.Departamento, id=formulario['departamento'].value())
                usuario.departamento=departamento
                # print(grupos)
                # print(usuario.groups)
                usuario.save()
                print(usuario.groups)
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

@login_required
def listar_problemas(request):
    # if request.user.has_perm('process.add_respuestaproblema'):
    reportes = []
    if request.user.is_superuser or request.user.has_perm('process.add_respuestaproblema') :
        reportes = models.ReportarProblema.objects.all()
    else:
        user = request.user
        tareas = models.Tarea.objects.filter(usuario=user)
        for t in tareas:
            print(t)
            try:
                r = models.ReportarProblema.objects.get(tarea=t)
                reportes.append(r)
            except:
                pass
        print(reportes)
        
    
    data = {
    'reportes': reportes,
    }   
    return render(request, 'process/problemas/listar_problemas.html', data)
    
@login_required
def responder_problema(request, id):
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
    if request.user.has_perm('process.add_respuestaproblema'):
        if reporte.estado == False:
            if request.method=='POST':
                    formulario = forms.SolucionProblemaForm(data=request.POST, files=request.FILES)
                    if formulario.is_valid():
                        respuesta.respuesta = formulario['respuesta'].value()
                        respuesta.problema = reporte
                        reporte.estado = True
                        reporte.save()
                        respuesta.save()    
                        messages.success(request, "Problema respondido correctamente")
                        return redirect(to="responder_problema",id=reporte.id)

                    else:
                        data["form"] = formulario
        else:
            data["formSolucion"] = forms.SolucionProblemaOkForm(instance=respuesta)             
        return render(request, 'process/problemas/responder_problema.html', data)
    else:
        data["formSolucion"] = forms.SolucionProblemaOkForm(instance=respuesta)
        return render(request, 'process/problemas/responder_problema.html', data)


##Gestión de departamentos.
@login_required
def agregar_departamento(request):
    if request.user.has_perm('process.add_departamento'):
        data = {
                'form': forms.DepartamentoForm()
        }
        if request.method == 'POST':
            formulario = forms.DepartamentoForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                formulario.save()
                data["mensaje"] = "Guardado correctamente."
            else:
                data["form"] = formulario

        return render(request,'process/departamento/agregar_departamento.html', data)
    else:
        return render(request,'process/error_permiso.html')

@login_required
def listar_departamento(request):
    
    departamentos = models.Departamento.objects.all()
    for d in departamentos:
        usuarios_depto = models.User.objects.filter(departamento=d).count()
        d.cant_usuarios = usuarios_depto
        d.save()            

    data = {
    'departamentos': departamentos,
    }   

    lita = listar_tareas_departamento(1,0)

    return render(request,'process/departamento/listar_departamento.html', data)

@login_required
def modificar_departamento(request,id):
    
    departamento = get_object_or_404(models.Departamento, id=id)
    data={
        'form': forms.DepartamentoForm(instance=departamento),
        'departamento':departamento,
    }
    if request.method == 'POST':
        formulario = forms.DepartamentoForm(data=request.POST, instance=departamento, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listar_departamentos")
        data["form"] = formulario
    return render(request,'process/departamento/modificar_departamento.html', data)

##Estadisticas
@login_required
def estadisticas_departamento(request, id):
    actualizar_semaforo()
    if request.user.has_perm('process.view_estadistica'):
        departamento = get_object_or_404(models.Departamento, id=id)
        porcentajes=[]
        porcentaje_estado_tareas=[]

        ##Tareas total departamento.
        tareas_departamento = listar_tareas_departamento_total(departamento.id)
        can_tareas_depto = len(tareas_departamento)

        ##Tareas departamento realizadas.
        tareas_departamento_realizadas = listar_tareas_departamento(departamento.id,1)
        can_tareas_realizadas = len(tareas_departamento_realizadas)
        

        ##Tareas departamento sin realizar.
        tareas_departamento_no_realizadas = listar_tareas_departamento(departamento.id,0)
        can_tareas_no_realizadas = len(tareas_departamento_no_realizadas)
        

        ##Usuarios por departamento.
        usuarios_departamento = listar_usuarios_departamento(departamento.id)

        try:
            ##Porcentajes

            porcentaje_tareas_realizada = (can_tareas_realizadas*100)/can_tareas_depto
            porcentajes.append(porcentaje_tareas_realizada)
            porcentaje_tareas_no_realizada = (can_tareas_no_realizadas*100)/can_tareas_depto
            porcentajes.append(porcentaje_tareas_no_realizada)
            
            estado_tarea_rojo = listar_estado_tareas_departamento(departamento.id,0,'r')
            estado_tarea_amarilla = listar_estado_tareas_departamento(departamento.id,0,'a')
            estado_tarea_verde = listar_estado_tareas_departamento(departamento.id,0,'v')

            porcentaje_estado_rojo = (len(estado_tarea_rojo)*100)/can_tareas_no_realizadas
            porcentaje_estado_amarilla = (len(estado_tarea_amarilla)*100)/can_tareas_no_realizadas
            porcentaje_estado_verde = (len(estado_tarea_verde)*100)/can_tareas_no_realizadas
            porcentaje_estado_tareas.append(porcentaje_estado_rojo)
            porcentaje_estado_tareas.append(porcentaje_estado_amarilla)
            porcentaje_estado_tareas.append(porcentaje_estado_verde)
        except:
            pass

        data = {
            'departamento': departamento,
            'tareas_departamento':tareas_departamento,
            'can_tareas_depto':can_tareas_depto,
            'tareas_departamento_realizadas': tareas_departamento_realizadas,
            'can_tareas_realizadas':can_tareas_realizadas,
            'tareas_departamento_no_realizadas':tareas_departamento_no_realizadas,
            'can_tareas_no_realizadas':can_tareas_no_realizadas,
            'usuarios_departamento':usuarios_departamento,
            'porcentajes':porcentajes,
            'porcentaje_estado_tareas':porcentaje_estado_tareas,
        }

        return render(request,'process/estadisticas/estadistica_departamento.html', data)
    else:
        return render(request,'process/error_permiso.html')

   
    

@login_required
def listar_departamento_estadistica(request):
    if request.user.has_perm('process.view_estadistica'):
        departamentos = models.Departamento.objects.all()
        for d in departamentos:
            usuarios_depto = models.User.objects.filter(departamento=d).count()
            d.cant_usuarios = usuarios_depto
            d.save()
    else:
        return render(request,'process/error_permiso.html')

    data = {
    'departamentos': departamentos,
    }   
    

    return render(request,'process/estadisticas/listar_departamento_estadisticas.html', data)

@login_required
def listar_grupo_estadistica(request):
    if request.user.has_perm('process.view_estadistica'):
        grupos = listar_grupos()
        data = {
            'grupos': grupos,
        }   
        
        return render(request,'process/estadisticas/listar_grupo_estadistica.html', data)
    else:
        return render(request,'process/error_permiso.html')

    


    

@login_required
def estadisticas_grupo(request,id):
    actualizar_semaforo()
    if request.user.has_perm('process.view_estadistica'):
        grupo = get_object_or_404(Group, id=id)
        tareas_no_realizada = []
        tareas_realizada = []
        porcentajes = []
        porcentaje_estado_tareas=[]
        
        tareas_grupo = listar_tareas_grupo(id)
        
        for t in tareas_grupo:
            if t[2] == 0:
                tareas_no_realizada.append(t)
            elif t[2] == 1:
                tareas_realizada.append(t)
        can_tareas_grupo = len(tareas_grupo)
        can_tareas_no_realizadas = len(tareas_no_realizada)
        can_tareas_realizadas = len(tareas_realizada)

        usuarios_grupo = listar_usuarios_grupo(id)
        
        try:
            ##Porcentajes
            porcentaje_tareas_no_realizada = (can_tareas_no_realizadas*100)/can_tareas_grupo
            porcentaje_tareas_realizada = (can_tareas_realizadas*100)/can_tareas_grupo
            porcentajes.append(porcentaje_tareas_realizada)
            porcentajes.append(porcentaje_tareas_no_realizada)
            
            ##Porcentaje estado tarea
            estado_tarea_rojo = listar_estado_tareas_grupo(id,0,'r')
            estado_tarea_amarilla = listar_estado_tareas_grupo(id,0,'a')
            estado_tarea_verde = listar_estado_tareas_grupo(id,0,'v')

            porcentaje_estado_rojo = (len(estado_tarea_rojo)*100)/can_tareas_no_realizadas
            porcentaje_estado_amarilla = (len(estado_tarea_amarilla)*100)/can_tareas_no_realizadas
            porcentaje_estado_verde = (len(estado_tarea_verde)*100)/can_tareas_no_realizadas
            porcentaje_estado_tareas.append(porcentaje_estado_rojo)
            porcentaje_estado_tareas.append(porcentaje_estado_amarilla)
            porcentaje_estado_tareas.append(porcentaje_estado_verde)
        except:
            pass

        
        data = {
            'grupo':grupo,
            'tareas_grupo':tareas_grupo,
            'tareas_no_realizada':tareas_no_realizada,
            'can_tareas_grupo':can_tareas_grupo,
            'can_tareas_no_realizadas':can_tareas_no_realizadas,
            'tareas_realizada':tareas_realizada,
            'can_tareas_realizadas':can_tareas_realizadas,
            'usuarios_grupo':usuarios_grupo,
            'porcentajes':porcentajes,
            'porcentaje_estado_tareas':porcentaje_estado_tareas


        }

        return render(request,'process/estadisticas/estadistica_grupo.html', data)
    else:
        return render(request,'process/error_permiso.html')

@login_required()
def listar_usuario_estadistica(request):
    user = request.user
    if request.user.is_superuser or request.user.has_perm('process.view_estadistica'):
        usuarios = models.User.objects.all()
    else:
        usuarios = models.User.objects.filter(id=user.id)

    data = {
    'usuarios': usuarios,
    }   


    return render(request,'process/estadisticas/listar_usuario_estadistica.html', data)

@login_required
def estadisticas_usuario(request,id):
    user = request.user
    actualizar_semaforo()
    if request.user.has_perm('process.view_estadistica') or int(user.id) == int(id):
        usuario = get_object_or_404(models.User, id=id)
        tareas_usuarios = listar_tareas_usuario(id)
        tareas_realizada = []
        tareas_no_realizada = []
        porcentajes = []
        porcentaje_estado_tareas=[]
        estado_tarea_rojo = []
        estado_tarea_amarilla = []
        estado_tarea_verde = []
        for t in tareas_usuarios:
            if t[2]==0:
                tareas_no_realizada.append(t)
            elif t[2] ==1:
                tareas_realizada.append(t)
        
        ##Cantidad de tareas del usuario.
        can_tareas_usuario = len(tareas_usuarios)
        can_tareas_no_realizadas = len(tareas_no_realizada)
        can_tareas_realizadas = len(tareas_realizada)

        ##Porcentajes
        try:
            
            porcentaje_tareas_no_realizada = (can_tareas_no_realizadas*100)/can_tareas_usuario
            porcentaje_tareas_realizada = (can_tareas_realizadas*100)/can_tareas_usuario
            porcentajes.append(porcentaje_tareas_realizada)
            porcentajes.append(porcentaje_tareas_no_realizada)
            
            for t in tareas_no_realizada:
                if t[6] == 'r':
                    estado_tarea_rojo.append(t)
                elif t[6] == 'a':
                    estado_tarea_amarilla.append(t)
                elif t[6] == 'v':
                    estado_tarea_verde.append(t)

            porcentaje_estado_rojo = (len(estado_tarea_rojo)*100)/can_tareas_no_realizadas
            porcentaje_estado_amarilla = (len(estado_tarea_amarilla)*100)/can_tareas_no_realizadas
            porcentaje_estado_verde = (len(estado_tarea_verde)*100)/can_tareas_no_realizadas
            porcentaje_estado_tareas.append(porcentaje_estado_rojo)
            porcentaje_estado_tareas.append(porcentaje_estado_amarilla)
            porcentaje_estado_tareas.append(porcentaje_estado_verde)
        except:
            pass
        data = {
            'usuario':usuario,
            'can_tareas_usuario':can_tareas_usuario,
            'can_tareas_no_realizadas':can_tareas_no_realizadas,
            'can_tareas_realizadas':can_tareas_realizadas,
            'tareas_no_realizada':tareas_no_realizada,
            'tareas_realizada':tareas_realizada,
            'porcentaje_estado_tareas':porcentaje_estado_tareas,
            'porcentajes':porcentajes
        }

        return render(request,'process/estadisticas/estadistica_usuario.html', data)
    else:
        return render(request,'process/error_permiso.html')

@login_required()
def estadistica_general(request):
    actualizar_semaforo()
    if request.user.has_perm('process.view_estadistica'):
        tareas = []
        porcentajes = []
        porcentajes_depto = []
        porcentajes_grupo = []
        porcentajes_usuario = []

        suma = 0
        ##Contar tareas totales.
        tareas_realizadas = listar_tareas_bd(1,1,1)
        tareas_sin_realizar = listar_tareas_bd(0,1,1)
        tareas_sin_asignar = listar_tareas_sin_asignar()
        for t in tareas_realizadas:
            tareas.append(t)
        for r in tareas_sin_realizar:
            tareas.append(r)
        
        
        cant_tareas_totales_asignadas = len(tareas)
        cant_tareas_sin_asignar = len(tareas_sin_asignar)
        cant_tareas_totales = cant_tareas_totales_asignadas + cant_tareas_sin_asignar
        cant_tareas_realizadas = len(tareas_realizadas)
        cant_tareas_sin_realizar = len(tareas_sin_realizar)

        

        try:
            ##Porcentajes

            porcentaje_tareas_realizada = (cant_tareas_realizadas*100)/cant_tareas_totales_asignadas
            porcentajes.append(porcentaje_tareas_realizada)
            porcentaje_tareas_no_realizada = (cant_tareas_sin_realizar*100)/cant_tareas_totales_asignadas
            porcentajes.append(porcentaje_tareas_no_realizada)

            porcentaje_tareas_asignadas = (cant_tareas_totales_asignadas*100)/cant_tareas_totales
            porcentaje_tareas_no_asignadas = (cant_tareas_sin_asignar*100)/cant_tareas_totales
            porcentajes.append(porcentaje_tareas_asignadas)
            porcentajes.append(porcentaje_tareas_no_asignadas)

            ##Porcentajes tareas asignadas por departamento.
            tareas_depto = contar_tareas_total_depto()
            for y in tareas_depto:
                suma = suma + y[0]
                
            for p in tareas_depto:
                x = (p[0]*100)/suma
                lista = []
                lista.append(x)
                lista.append(p[2])
                lista.append(p[0])
                lista.append(p[1])
                porcentajes_depto.append(lista)
            
            ##Porcentajes tareas asignadas por grupo
            tareas_grupo = contar_tareas_total_grupo()
            suma = 0
            for y in tareas_grupo:
                suma = suma + y[0]
                print(suma)  
            for p in tareas_grupo:
                x = (p[0]*100)/suma
                lista = []
                lista.append(x)
                lista.append(p[2])
                lista.append(p[0])
                lista.append(p[1])
                porcentajes_grupo.append(lista)
            

            ##Porcentajes tareas asignadas usuarios.
            tareas_usuario = contar_tareas_total_usuario()
            suma = 0
            for y in tareas_usuario:
                suma = suma + y[0]
                print(suma)  
            for p in tareas_usuario:
                x = (p[0]*100)/suma
                lista = []
                lista.append(x)
                lista.append(p[2])
                lista.append(p[0])
                lista.append(p[1])
                porcentajes_usuario.append(lista)
            print(porcentajes_usuario)
        except:
            pass

        # print(tareas_depto)
        
        # print (tareas_sin_asignar) 
        data = {
            'cant_tareas_totales_asignadas':cant_tareas_totales_asignadas,
            'cant_tareas_realizadas':cant_tareas_realizadas,
            'cant_tareas_totales':cant_tareas_totales,
            'cant_tareas_sin_realizar':cant_tareas_sin_realizar,
            'cant_tareas_sin_asignar':cant_tareas_sin_asignar,
            
            ##Porcentajes
            'porcentajes':porcentajes,
            'porcentajes_depto':porcentajes_depto,
            'porcentajes_grupo':porcentajes_grupo,
            'porcentajes_usuario':porcentajes_usuario,
        

        }
        return render(request,'process/estadisticas/estadistica_general.html',data)
    else:
        return render(request,'process/error_permiso.html')

##Métodos de pl/sql
def listar_tareas_departamento(id_departamento, realizado):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_TAREAS_DEPARTAMENTO',[id_departamento,realizado,out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)
    
    return lista

def listar_tareas_departamento_total(id_departamento):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_TAREAS_DEPARTAMENTO_TOTAL',[id_departamento,out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)
    
    return lista

def listar_usuarios_departamento(id_departamento):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_USUARIOS_DEPARTAMENTO',[id_departamento,out_cur])
    
    lista= []
    for l in out_cur:
        lista.append(l)

    return lista

def listar_estado_tareas_departamento(id_departamento, realizado, estado):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_ESTADO_TAREAS',[id_departamento,realizado,estado,out_cur])
    
    lista= []
    for l in out_cur:
        lista.append(l)

    return lista

def listar_grupos():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_GRUPOS',[out_cur])
    
    lista= []
    for l in out_cur:
        lista.append(l)

    return lista

def listar_tareas_grupo(id_grupo):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_TAREAS_GRUPO',[id_grupo,out_cur])
    
    lista = []
    for l in out_cur:
        lista.append(l)
    return lista

def listar_usuarios_grupo(id_grupo):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_USUARIOS_GRUPO',[id_grupo,out_cur])

    lista = []
    for l in out_cur:
        lista.append(l)
    return lista

def listar_estado_tareas_grupo(id_grupo, realizado, estado):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_ESTADO_TAREAS_GRUPO',[id_grupo,realizado,estado,out_cur])
    
    lista= []
    for l in out_cur:
        lista.append(l)

    return lista

def listar_tareas_usuario(id_usuario):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_TAREAS_USUARIO',[id_usuario,out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)
    
    return lista
    # SP_LISTAR_TAREAS_GRUPO

def listar_tareas_sin_asignar():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_LISTAR_TAREAS_SIN_ASIGNAR',[out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)
    
    return lista

def contar_tareas_total_depto():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_CONTAR_TAREAS_DEPTOS',[out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)
    
    return lista

def contar_tareas_total_grupo():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_CANT_TAREAS_GRUPOS_TOTAL',[out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)
    
    return lista

def contar_tareas_total_usuario():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    cursor.callproc('SP_CONTAR_TAREAS_USUARIOS',[out_cur])

    lista = []

    for l in out_cur:
        lista.append(l)

    return lista

@login_required()
def perfil_usuario(request):
    user = request.user
    departamento = ()
    try:
        departamento = models.Departamento.objects.get(id=user.departamento.id)
    except:
        pass
    try:
        print(user.groups.first())
        grupo = Group.objects.get(id=user.groups.first().id)
        print(grupo)
    except:
        pass

    
    data = {
        'user':user,
        'departamento':departamento,
        'grupo':grupo,
    }
    return render(request, 'registration/perfil_usuario.html',data)

def reporte_estadistica_departamento(request, id):
    actualizar_semaforo()
    departamento = get_object_or_404(models.Departamento, id=id)
    porcentajes=[]
    porcentaje_estado_tareas=[]

    ##Tareas total departamento.
    tareas_departamento = listar_tareas_departamento_total(departamento.id)
    can_tareas_depto = len(tareas_departamento)

    ##Tareas departamento realizadas.
    tareas_departamento_realizadas = listar_tareas_departamento(departamento.id,1)
    can_tareas_realizadas = len(tareas_departamento_realizadas)
    

    ##Tareas departamento sin realizar.
    tareas_departamento_no_realizadas = listar_tareas_departamento(departamento.id,0)
    can_tareas_no_realizadas = len(tareas_departamento_no_realizadas)
    

    ##Usuarios por departamento.
    usuarios_departamento = listar_usuarios_departamento(departamento.id)

    try:
        ##Porcentajes

        porcentaje_tareas_realizada = (can_tareas_realizadas*100)/can_tareas_depto
        porcentajes.append(porcentaje_tareas_realizada)
        porcentaje_tareas_no_realizada = (can_tareas_no_realizadas*100)/can_tareas_depto
        porcentajes.append(porcentaje_tareas_no_realizada)
        
        estado_tarea_rojo = listar_estado_tareas_departamento(departamento.id,0,'r')
        estado_tarea_amarilla = listar_estado_tareas_departamento(departamento.id,0,'a')
        estado_tarea_verde = listar_estado_tareas_departamento(departamento.id,0,'v')

        porcentaje_estado_rojo = (len(estado_tarea_rojo)*100)/can_tareas_no_realizadas
        porcentaje_estado_amarilla = (len(estado_tarea_amarilla)*100)/can_tareas_no_realizadas
        porcentaje_estado_verde = (len(estado_tarea_verde)*100)/can_tareas_no_realizadas
        porcentaje_estado_tareas.append(porcentaje_estado_rojo)
        porcentaje_estado_tareas.append(porcentaje_estado_amarilla)
        porcentaje_estado_tareas.append(porcentaje_estado_verde)
    except:
        pass

    template_path = 'process/pdf/reporte_estadistica.html'

    context = {
        'departamento': departamento,
        'tareas_departamento':tareas_departamento,
        'can_tareas_depto':can_tareas_depto,
        'tareas_departamento_realizadas': tareas_departamento_realizadas,
        'can_tareas_realizadas':can_tareas_realizadas,
        'tareas_departamento_no_realizadas':tareas_departamento_no_realizadas,
        'can_tareas_no_realizadas':can_tareas_no_realizadas,
        'usuarios_departamento':usuarios_departamento,
        'porcentajes':porcentajes,
        'porcentaje_estado_tareas':porcentaje_estado_tareas,

    }

    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="estadistica_departamento.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def reporte_estadistica_grupo(request,id):
    actualizar_semaforo()
    grupo = get_object_or_404(Group, id=id)
    tareas_no_realizada = []
    tareas_realizada = []
    porcentajes = []
    porcentaje_estado_tareas=[]

    tareas_grupo = listar_tareas_grupo(id)
    
    for t in tareas_grupo:
        if t[2] == 0:
            tareas_no_realizada.append(t)
        elif t[2] == 1:
            tareas_realizada.append(t)
    can_tareas_grupo = len(tareas_grupo)
    can_tareas_no_realizadas = len(tareas_no_realizada)
    can_tareas_realizadas = len(tareas_realizada)

    usuarios_grupo = listar_usuarios_grupo(id)
    
    try:
        ##Porcentajes
        porcentaje_tareas_no_realizada = (can_tareas_no_realizadas*100)/can_tareas_grupo
        porcentaje_tareas_realizada = (can_tareas_realizadas*100)/can_tareas_grupo
        porcentajes.append(porcentaje_tareas_realizada)
        porcentajes.append(porcentaje_tareas_no_realizada)
        
        ##Porcentaje estado tarea
        estado_tarea_rojo = listar_estado_tareas_grupo(id,0,'r')
        estado_tarea_amarilla = listar_estado_tareas_grupo(id,0,'a')
        estado_tarea_verde = listar_estado_tareas_grupo(id,0,'v')

        porcentaje_estado_rojo = (len(estado_tarea_rojo)*100)/can_tareas_no_realizadas
        porcentaje_estado_amarilla = (len(estado_tarea_amarilla)*100)/can_tareas_no_realizadas
        porcentaje_estado_verde = (len(estado_tarea_verde)*100)/can_tareas_no_realizadas
        porcentaje_estado_tareas.append(porcentaje_estado_rojo)
        porcentaje_estado_tareas.append(porcentaje_estado_amarilla)
        porcentaje_estado_tareas.append(porcentaje_estado_verde)
    except:
        pass

    
    context = {
        'grupo':grupo,
        'tareas_grupo':tareas_grupo,
        'tareas_no_realizada':tareas_no_realizada,
        'can_tareas_grupo':can_tareas_grupo,
        'can_tareas_no_realizadas':can_tareas_no_realizadas,
        'tareas_realizada':tareas_realizada,
        'can_tareas_realizadas':can_tareas_realizadas,
        'usuarios_grupo':usuarios_grupo,
        'porcentajes':porcentajes,
        'porcentaje_estado_tareas':porcentaje_estado_tareas


    }
    template_path = 'process/pdf/reportes_estadistica_grupo.html'

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="estadistica_departamento.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def reporte_estadistica_usuario(request,id):
    actualizar_semaforo()
    usuario = get_object_or_404(models.User, id=id)
    tareas_usuarios = listar_tareas_usuario(id)
    tareas_realizada = []
    tareas_no_realizada = []
    porcentajes = []
    porcentaje_estado_tareas=[]
    estado_tarea_rojo = []
    estado_tarea_amarilla = []
    estado_tarea_verde = []
    for t in tareas_usuarios:
        if t[2]==0:
            tareas_no_realizada.append(t)
        elif t[2] ==1:
            tareas_realizada.append(t)
    
    ##Cantidad de tareas del usuario.
    can_tareas_usuario = len(tareas_usuarios)
    can_tareas_no_realizadas = len(tareas_no_realizada)
    can_tareas_realizadas = len(tareas_realizada)

    ##Porcentajes
    try:
        
        porcentaje_tareas_no_realizada = (can_tareas_no_realizadas*100)/can_tareas_usuario
        porcentaje_tareas_realizada = (can_tareas_realizadas*100)/can_tareas_usuario
        porcentajes.append(porcentaje_tareas_realizada)
        porcentajes.append(porcentaje_tareas_no_realizada)
        
        for t in tareas_no_realizada:
            if t[6] == 'r':
                estado_tarea_rojo.append(t)
            elif t[6] == 'a':
                estado_tarea_amarilla.append(t)
            elif t[6] == 'v':
                estado_tarea_verde.append(t)

        porcentaje_estado_rojo = (len(estado_tarea_rojo)*100)/can_tareas_no_realizadas
        porcentaje_estado_amarilla = (len(estado_tarea_amarilla)*100)/can_tareas_no_realizadas
        porcentaje_estado_verde = (len(estado_tarea_verde)*100)/can_tareas_no_realizadas
        porcentaje_estado_tareas.append(porcentaje_estado_rojo)
        porcentaje_estado_tareas.append(porcentaje_estado_amarilla)
        porcentaje_estado_tareas.append(porcentaje_estado_verde)
    except:
        pass
    context = {
        'usuario':usuario,
        'can_tareas_usuario':can_tareas_usuario,
        'can_tareas_no_realizadas':can_tareas_no_realizadas,
        'can_tareas_realizadas':can_tareas_realizadas,
        'tareas_no_realizada':tareas_no_realizada,
        'tareas_realizada':tareas_realizada,
        'porcentaje_estado_tareas':porcentaje_estado_tareas,
        'porcentajes':porcentajes
    }
    template_path = 'process/pdf/reporte_estadistica_usuario.html'

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="estadistica_usuario.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def reporte_estadistica_general(request):
    actualizar_semaforo()

    tareas = []
    porcentajes = []
    porcentajes_depto = []
    porcentajes_grupo = []
    porcentajes_usuario = []

    suma = 0
    ##Contar tareas totales.
    tareas_realizadas = listar_tareas_bd(1,1,1)
    tareas_sin_realizar = listar_tareas_bd(0,1,1)
    tareas_sin_asignar = listar_tareas_sin_asignar()
    for t in tareas_realizadas:
        tareas.append(t)
    for r in tareas_sin_realizar:
        tareas.append(r)
    
    
    cant_tareas_totales_asignadas = len(tareas)
    cant_tareas_sin_asignar = len(tareas_sin_asignar)
    cant_tareas_totales = cant_tareas_totales_asignadas + cant_tareas_sin_asignar
    cant_tareas_realizadas = len(tareas_realizadas)
    cant_tareas_sin_realizar = len(tareas_sin_realizar)

    

    try:
        ##Porcentajes

        porcentaje_tareas_realizada = (cant_tareas_realizadas*100)/cant_tareas_totales_asignadas
        porcentajes.append(porcentaje_tareas_realizada)
        porcentaje_tareas_no_realizada = (cant_tareas_sin_realizar*100)/cant_tareas_totales_asignadas
        porcentajes.append(porcentaje_tareas_no_realizada)

        porcentaje_tareas_asignadas = (cant_tareas_totales_asignadas*100)/cant_tareas_totales
        porcentaje_tareas_no_asignadas = (cant_tareas_sin_asignar*100)/cant_tareas_totales
        porcentajes.append(porcentaje_tareas_asignadas)
        porcentajes.append(porcentaje_tareas_no_asignadas)

        ##Porcentajes tareas asignadas por departamento.
        tareas_depto = contar_tareas_total_depto()
        for y in tareas_depto:
            suma = suma + y[0]
            
        for p in tareas_depto:
            x = (p[0]*100)/suma
            lista = []
            lista.append(x)
            lista.append(p[2])
            lista.append(p[0])
            lista.append(p[1])
            porcentajes_depto.append(lista)
        
        ##Porcentajes tareas asignadas por grupo
        tareas_grupo = contar_tareas_total_grupo()
        suma = 0
        for y in tareas_grupo:
            suma = suma + y[0]
            print(suma)  
        for p in tareas_grupo:
            x = (p[0]*100)/suma
            lista = []
            lista.append(x)
            lista.append(p[2])
            lista.append(p[0])
            lista.append(p[1])
            porcentajes_grupo.append(lista)
        

        ##Porcentajes tareas asignadas usuarios.
        tareas_usuario = contar_tareas_total_usuario()
        suma = 0
        for y in tareas_usuario:
            suma = suma + y[0]
            print(suma)  
        for p in tareas_usuario:
            x = (p[0]*100)/suma
            lista = []
            lista.append(x)
            lista.append(p[2])
            lista.append(p[0])
            lista.append(p[1])
            porcentajes_usuario.append(lista)
        print(porcentajes_usuario)
    except:
        pass

    # print(tareas_depto)
    
    # print (tareas_sin_asignar) 
    context = {
        'cant_tareas_totales_asignadas':cant_tareas_totales_asignadas,
        'cant_tareas_realizadas':cant_tareas_realizadas,
        'cant_tareas_totales':cant_tareas_totales,
        'cant_tareas_sin_realizar':cant_tareas_sin_realizar,
        'cant_tareas_sin_asignar':cant_tareas_sin_asignar,
        
        ##Porcentajes
        'porcentajes':porcentajes,
        'porcentajes_depto':porcentajes_depto,
        'porcentajes_grupo':porcentajes_grupo,
        'porcentajes_usuario':porcentajes_usuario,
    

    }
    template_path = 'process/pdf/reporte_estadistica_general.html'

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="estadistica_usuario.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response