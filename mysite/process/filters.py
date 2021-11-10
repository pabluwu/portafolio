import django_filters
from django_filters import DateFilter

from . import models

class TareaFilter(django_filters.FilterSet):
    class Meta:
        model = models.Tarea
        fields = '__all__'
        exclude = ['nombre', 'descripcion', 'fechaCreacion', 'fechaTermino', 'fechaLimite', 'realizado']