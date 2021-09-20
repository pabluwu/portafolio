from django.db import models
from datetime import datetime, date

class Tarea(models.Model):
    nombre = models.CharField(max_length=50, blank=False)
    descripcion = models.TextField(blank=False)
    realizado = models.BooleanField(default=False)
    fechaCreacion = models.DateTimeField(auto_now_add=True, auto_now=False)
    
    def __str__(self):
        return self.nombre
   

class FlujoTarea(models.Model):
    nombre = models.CharField(max_length=50)
    tareas = models.ManyToManyField(Tarea)
    def __str__(self):
        return self.nombre

class Perrito(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre
    
    
"""     tarea = models.ForeignKey(Tarea, null=True, on_delete=models.PROTECT)  """
    
""" 
class FlujoTarea_Tarea(models.Model):
    FlujoTarea = models.ForeignKey(FlujoTarea, on_delete=models.PROTECT)
    Tarea = models.ForeignKey(Tarea, on_delete=models.PROTECT)  

    def __str__(self):
        return self.FlujoTarea  """

