from django.db import models
from datetime import datetime, date
from django.contrib.auth.models import User

class Tarea(models.Model):
    nombre = models.CharField(max_length=50, blank=False)
    descripcion = models.TextField(blank=False)
    realizado = models.BooleanField(default=False)
    fechaCreacion = models.DateField(auto_now_add=True, auto_now=False)
    fechaLimite = models.DateField(default=datetime.now)
    fechaTermino = models.DateField(default=datetime.now)
    usuario = models.ForeignKey(User, null=True, on_delete=models.PROTECT)

    
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

class Semáforo(models.Model):
        

"""     tarea = models.ForeignKey(Tarea, null=True, on_delete=models.PROTECT)  """
    
""" 
class FlujoTarea_Tarea(models.Model):
    FlujoTarea = models.ForeignKey(FlujoTarea, on_delete=models.PROTECT)
    Tarea = models.ForeignKey(Tarea, on_delete=models.PROTECT)  

    def __str__(self):
        return self.FlujoTarea  """


