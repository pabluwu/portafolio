from django.db import models
from datetime import datetime, date, timedelta
from django.contrib.auth.models import User, AbstractUser

class Departamento(models.Model):
    nombre = models.CharField(max_length=50, blank=False)
    descripcion = models.TextField(blank=True)
    fechaCreacion = models.DateField(auto_now_add=True, auto_now=False)
    cant_usuarios = models.IntegerField(blank=True, default=0)
    def __str__(self):
        return self.nombre
   
class User(AbstractUser):
    departamento = models.ForeignKey(Departamento, null=True, on_delete=models.PROTECT)

class Tarea(models.Model):
    nombre = models.CharField(max_length=50, blank=False)
    descripcion = models.TextField(blank=False)
    realizado = models.BooleanField(default=False)
    is_tipo = models.BooleanField(default=False)
    fechaCreacion = models.DateField(auto_now_add=True, auto_now=False)
    fechaLimite = models.DateField(default=datetime.now)
    fechaTermino = models.DateField(default=datetime.now)
    usuario = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    tarea_parent = models.ForeignKey('self', null=True, default=None, on_delete=models.PROTECT)

    
    def __str__(self):
        return self.nombre

class FlujoTarea(models.Model):
    nombre = models.CharField(max_length=50)
    tareas = models.ManyToManyField(Tarea)
    def __str__(self):
        return self.nombre
    
class MotivoRechazo(models.Model):
    descripcion = models.TextField(blank=False)
    respondido = models.BooleanField(default=False)
    fechaCreacion = models.DateField(auto_now_add=True, auto_now=False)
    usuario = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    tarea = models.ForeignKey(Tarea, on_delete=models.PROTECT)

    def __str__(self):
        return self.descripcion

class RespuestaRechazo(models.Model):
    respuesta = models.TextField(blank=False, null=True)
    fechaRespuesta = models.DateField(auto_now_add=True, auto_now=False)
    aceptado = models.BooleanField(default=False)
    motivoRechazo = models.ForeignKey(MotivoRechazo, on_delete=models.PROTECT)

    def __str__(self):
        return self.respuesta
    
class CalculoEstado(models.Model):
    fechaActualCalculo = models.DateField(auto_now_add=True, auto_now=False)
    diasRestantes = models.DurationField(default=timedelta())
    tarea = models.ForeignKey(Tarea, on_delete=models.PROTECT)

    def __str__(self):

        return str(self.pk)


class Semaforo(models.Model):
    estadoSemaforo = models.CharField(blank=False, null=True, max_length=2)
    semaforoRojo = models.DurationField(default=timedelta())
    calculoEstado = models.ForeignKey(CalculoEstado, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.pk)

class ReportarProblema(models.Model):
    descripcion = models.TextField(blank=False)
    estado = models.BooleanField(default=False) #Solucionado / No Solucionado
    fechaCreacion = models.DateField(auto_now_add=True, auto_now=False)
    tarea = models.ForeignKey(Tarea, on_delete=models.PROTECT)

    def __str__(self):
        return self.descripcion 

class RespuestaProblema(models.Model):
    respuesta = models.TextField(blank=False, null=True)
    fechaRespuesta = models.DateField(auto_now_add=True, auto_now=False)
    problema = models.ForeignKey(ReportarProblema, on_delete=models.PROTECT)
    

    def __str__(self):
        return self.respuesta

"""     tarea = models.ForeignKey(Tarea, null=True, on_delete=models.PROTECT)  """
    
""" 
class FlujoTarea_Tarea(models.Model):
    FlujoTarea = models.ForeignKey(FlujoTarea, on_delete=models.PROTECT)
    Tarea = models.ForeignKey(Tarea, on_delete=models.PROTECT)  

    def __str__(self):
        return self.FlujoTarea  """


