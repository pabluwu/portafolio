from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('',views.index, name="index"),
    path('proyecto',views.proyecto, name="proyecto"),
    path('login', auth_views.LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('agregar/flujo_tarea', views.agregar_flujo_tarea, name="agregar_flujo_tarea"),
    path('listar/flujo_tarea', views.listar_flujo_tareas, name="listar_flujo_tareas"),
    path('modificar/flujo_tarea/<id>', views.modificar_flujo_tarea, name="modificar_flujo_tarea"),
    path('agregar/tarea', views.agregar_tarea, name="agregar_tarea"),
    path('listar/tarea', views.listar_tareas, name="listar_tareas"),
    path('listar/tarea_completada', views.listar_tareas_completadas, name="listar_tareas_completadas"),
    path('modificar/tarea/<id>', views.modificar_tarea, name="modificar_tarea"),
    path('ver/tarea/<id>', views.tarea_completada, name="tarea_completada"),
    path('agregar/usuario', views.registrar_usuario, name="registrar_usuario"),
    path('listar/usuarios', views.listar_usuarios, name="listar_usuarios"),
    path('modificar/usuario/<id>', views.modificar_usuario_admin, name="modificar_usuario_admin"),
    path('agregar/grupo', views.agregar_grupo, name="agregar_grupo"),
    path('reportar_problema', views.reportar_problema, name="reportar_problema"),
    path('listar/reportes_problemas', views.listar_problemas, name="listar_reportes_problemas"),
    path('ver/problema/<id>', views.responder_problema, name = "responder_problema")
]