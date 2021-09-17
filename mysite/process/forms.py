from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ValidationError

from . import models

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Confirmar contraseña', widget=forms.PasswordInput)
    

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
        fields = '__all__'

class UserGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'permissions': FilteredSelectMultiple("Permission", False, attrs={'rows':'2'}),
        }

class GroupForm(forms.Form):
    nombre = forms.CharField(max_length=50)

class UsuarioFormulario(forms.Form):
    username = forms.CharField(max_length=50)
    nombre = forms.CharField(max_length=50)
    apellido = forms.CharField(max_length=50)
    email = forms.CharField(max_length=50)


    
