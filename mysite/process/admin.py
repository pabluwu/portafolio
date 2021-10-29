from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Tarea)
admin.site.register(models.FlujoTarea)
admin.site.register(models.MotivoRechazo)
admin.site.register(models.RespuestaRechazo)