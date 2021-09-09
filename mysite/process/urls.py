from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('',views.index),
    path('proyecto',views.proyecto, name="proyecto"),
    path('login', auth_views.LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('agregar/flujo_tarea', views.agregar_flujo_tarea, name="agregar_flujo_tarea"),
    path('agregar/tarea', views.agregar_tarea, name="agregar_flujo_tarea"),

]