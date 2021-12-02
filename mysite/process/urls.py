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
    path('listar/rechazos_tarea', views.listar_rechazos_tarea, name="listar_rechazos_tarea"),
    path('revisar_rechazo/<id>/<id_rechazo>', views.revisar_rechazo_tarea, name="revisar_rechazo_tarea"),
    # url(r'^viewspecs/itemdetails/(?P<param1>[\w-]+)/(?P<param2>[\w-]+)/$', views.specsView),
    path('listar/tarea_completada', views.listar_tareas_completadas, name="listar_tareas_completadas"),
    path('modificar/tarea/<id>', views.modificar_tarea, name="modificar_tarea"),
    path('ver/tarea/<id>', views.tarea_completada, name="tarea_completada"),
    path('agregar/usuario', views.registrar_usuario, name="registrar_usuario"),
    path('listar/usuarios', views.listar_usuarios, name="listar_usuarios"),
    path('modificar/usuario/<id>', views.modificar_usuario_admin, name="modificar_usuario_admin"),
    path('agregar/grupo', views.agregar_grupo, name="agregar_grupo"),
    path('reportar_problema', views.reportar_problema, name="reportar_problema"),
    path('listar/reportes_problemas', views.listar_problemas, name="listar_reportes_problemas"),
    path('ver/problema/<id>', views.responder_problema, name = "responder_problema"),
    path('agregar/departamento', views.agregar_departamento, name="agregar_departamento"),
    path('listar/departamentos', views.listar_departamento, name="listar_departamentos"),
    path('modificar/departamento/<id>', views.modificar_departamento, name="modificar_departamento"),

    path('estadisticas/departamento/<id>', views.estadisticas_departamento, name="estadistica_departamento"),
    path('estadisticas/listar/departamentos', views.listar_departamento_estadistica, name="listar_departamentos_estadisticas"),
    path('estadisticas/listar/grupos', views.listar_grupo_estadistica, name="listar_grupo_estadistica"),
    path('estadisticas/grupo/<id>', views.estadisticas_grupo, name="estadisticas_grupo"),
    path('estadisticas/listar/usuarios', views.listar_usuario_estadistica, name="listar_usuario_estadistica"),
    path('estadisticas/usuario/<id>', views.estadisticas_usuario, name="estadisticas_usuario"),
    path('estadistica/general', views.estadistica_general, name="estadistica_general"),

    path('perfil', views.perfil_usuario, name="perfil_usuario"),

    path('reporte_estadistica_departamento/<id>',views.reporte_estadistica_departamento, name="reporte_estadistica_departamento"),
    path('reporte_estadistica_grupo/<id>',views.reporte_estadistica_grupo, name="reporte_estadistica_grupo"),
    path('reporte_estadistica_usuario/<id>',views.reporte_estadistica_usuario, name="reporte_estadistica_usuario"),
    path('reporte_estadistica_general',views.reporte_estadistica_general, name="reporte_estadistica_general"),
    
    

    
]