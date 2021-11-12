from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Tarea)
admin.site.register(models.FlujoTarea)
admin.site.register(models.MotivoRechazo)
admin.site.register(models.RespuestaRechazo)
admin.site.register(models.CalculoEstado)
admin.site.register(models.Semaforo)
admin.site.register(models.User)
admin.site.register(models.Departamento)