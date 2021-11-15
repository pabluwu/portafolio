from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminDateWidget
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from . import models

class UserCreationForm(UserCreationForm):
    groups = forms.ModelChoiceField(queryset=Group.objects.all())
    pass
    class Meta:
        model = models.User
        fields=['username','first_name','last_name','email', 'departamento', 'groups']
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'groups': _('Grupo'),
        }
        widgets = {

        }

class RechazoForm(forms.ModelForm):
    class Meta:
        model = models.MotivoRechazo
        fields =['descripcion']

class RespuestaSolicitudForm(forms.ModelForm):
    class Meta:
        model = models.RespuestaRechazo
        fields = ['respuesta']

class RespuestaSolicitudRespondidaForm(forms.ModelForm):
    class Meta:
        model = models.RespuestaRechazo
        fields = ('respuesta', 'aceptado', 'motivoRechazo')
        labels = {
            'motivoRechazo': _('Solicitud de rechazo'),
        }
        widgets = {
            'respuesta' : forms.TextInput(attrs={'readonly':'readonly'}),
            'aceptado': forms.CheckboxInput(attrs={'disabled':'disabled'}),
            'motivoRechazo' : forms.TextInput(attrs={'readonly':'readonly'}),
        }

class SolicitudRechazoForm(forms.Form):

    descripcion = forms.CharField(max_length=50)
    usuario = forms.CharField(max_length=50)
    tarea = forms.CharField(max_length=50)
    descripcion.widget.attrs['readonly'] = True
    usuario.widget.attrs['readonly'] = True
    tarea.widget.attrs['readonly'] = True
    widgets = {
        'descripcion' : forms.TextInput(attrs={'readonly':'readonly'}),
        'usuario': forms.TextInput(attrs={'readonly':'readonly'}),
        'tarea': forms.TextInput(attrs={'readonly':'readonly'}),
    }


class FlujoTareaForm(forms.ModelForm):

    class Meta:
        model = models.FlujoTarea
        fields = '__all__'

class TareaForm(forms.ModelForm):
    
    class Meta:
        model = models.Tarea
        fields = ['nombre', 'descripcion', 'fechaLimite', 'usuario']

class TareaCompletaForm(forms.ModelForm):
    class Meta:
        model = models.Tarea
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'readonly':'readonly'}),
            'descripcion': forms.TextInput(attrs={'readonly':'readonly'}),
            'realizado': forms.CheckboxInput(attrs={'disabled':'disabled'}),
            'fechaCreacion': forms.DateInput(attrs={'readonly':'readonly'}),
            'fechaLimite': forms.DateInput(attrs={'readonly':'readonly'}),
            'fechaTermino': forms.DateInput(attrs={'readonly':'readonly'}),
            'usuario': forms.TextInput(attrs={'readonly':'readonly'}),
        }

class GroupForm(forms.Form):



    opciones_permisos = [
    ('add_tarea', 'Agregar Tarea'),
    ('change_tarea', 'Modificar Tarea'),
    ('add_flujotarea', 'Agregar flujo de tarea'),
    ('change_flujotarea', 'Modificar flujo de tarea'),
    ('add_respuestarechazo','Responder Solicitud Rechazo'),
    ('add_respuestaproblema','Responder Reportes'),
    ('add_departamento', 'Agregar Departamento'),
    ('change_departamento','Modificar Departamento'),
]
    nombre = forms.CharField(max_length=50)
    permisos = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=opciones_permisos,
    )

class UsuarioFormulario(forms.Form):
    username = forms.CharField(max_length=50)
    nombre = forms.CharField(max_length=50)
    apellido = forms.CharField(max_length=50)
    email = forms.CharField(max_length=50)
    grupos = forms.ModelChoiceField(queryset=Group.objects.all())
    departamento = forms.ModelChoiceField(queryset=models.Departamento.objects.all())


class ReportarProblemaForm(forms.ModelForm):
    class Meta:
        model = models.ReportarProblema
        fields =  ['descripcion',]

class RevisarReporteForm(forms.ModelForm):
    class Meta:
        model = models.ReportarProblema
        fields = ('descripcion', 'estado', 'tarea')
        widgets = {
            'descripcion' : forms.TextInput(attrs={'readonly':'readonly'}),
            'estado': forms.CheckboxInput(attrs={'disabled':'disabled'}),
            'tarea' : forms.TextInput(attrs={'readonly':'readonly'}),
        }

class SolucionProblemaForm(forms.ModelForm):
    class Meta:
        model = models.RespuestaProblema
        fields = ('respuesta',)

class SolucionProblemaOkForm(forms.ModelForm):
    class Meta:
        model = models.RespuestaProblema
        fields = ('respuesta',)
        widgets = {
            'respuesta' : forms.TextInput(attrs={'readonly':'readonly'}),
        }
    
class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = models.Departamento
        fields = ('nombre', 'descripcion')
