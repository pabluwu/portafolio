from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminDateWidget
from django.forms import ValidationError

from . import models

class UserCreationForm(UserCreationForm):
    pass
    """ password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Confirmar contraseña', widget=forms.PasswordInput)
     """
    class Meta:
        model = User
        fields=['username','first_name','last_name','email']

   


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

class UserGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'

class GroupForm(forms.Form):



    FAVORITE_COLORS_CHOICES = [
    ('add_tarea', 'Agregar Tarea'),
    ('change_tarea', 'Modificar Tarea'),
    ('add_flujotarea', 'Agregar flujo de tarea'),
    ('change_flujotarea', 'Modificar flujo de tarea'),
]
    nombre = forms.CharField(max_length=50)
    permisos = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=FAVORITE_COLORS_CHOICES,
    )

class UsuarioFormulario(forms.Form):
    
    FAVORITE_COLORS_CHOICES = [
    ('add_tarea', 'Agregar Tarea'),
    ('change_tarea', 'Modificar Tarea'),
    ('add_flujotarea', 'Agregar flujo de tarea'),
    ('change_flujotarea', 'Modificar flujo de tarea'),
]

    username = forms.CharField(max_length=50)
    nombre = forms.CharField(max_length=50)
    apellido = forms.CharField(max_length=50)
    email = forms.CharField(max_length=50)
    grupos = forms.ModelMultipleChoiceField(queryset=Group.objects.all(),widget=forms.CheckboxSelectMultiple)


    
