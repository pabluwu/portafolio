from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('',views.index),
    path('proyecto',views.proyecto, name="proyecto"),
    path('login', auth_views.LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('agregar/flujo_tarea', views.agregar_flujo_tarea, name="agregar_flujo_tarea"),
    path('agregar/tarea', views.agregar_tarea, name="agregar_tarea"),
    path('listar/tarea', views.listar_tareas, name="listar_tareas"),
    path('listar/flujo_tarea', views.listar_flujo_tareas, name="listar_flujo_tareas"),
    path('modificar/tarea/<id>', views.modificar_tarea, name="modificar_tarea"),
    path('modificar/flujo_tarea/<id>', views.modificar_flujo_tarea, name="modificar_flujo_tarea"),

]