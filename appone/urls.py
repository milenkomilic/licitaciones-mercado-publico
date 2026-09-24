from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Licitaciones diarias
    path('licitaciones/generales/', views.listar_licitaciones_generales, name='listar_licitaciones_generales'),
    path('licitaciones/priorizadas/', views.listar_licitaciones_priorizadas, name='listar_licitaciones_priorizadas'),
    path('licitaciones/detalle/<int:id>/', views.detalle_licitacion, name='detalle_licitacion'),

    # Licitaciones archivadas
    path('licitaciones/archivadas/', views.listar_licitaciones_archivadas, name='listar_licitaciones_archivadas'),
    path('licitaciones/archivadas/detalle/<int:id>/', views.detalle_licitacion_archivada, name='detalle_licitacion_archivada'),

    # Sectores
    path('sectores/', views.lista_sectores, name='lista_sectores'),
    path('sectores/crear/', views.crear_sector, name='crear_sector'),
    path('sectores/<int:sector_id>/editar/', views.editar_sector, name='editar_sector'),
    path('sectores/<int:sector_id>/eliminar/', views.eliminar_sector, name='eliminar_sector'),
    
    # Palabras Clave
    path('palabras-clave/admin/', views.gestionar_palabras_clave, name='gestionar_palabras_admin'),
    path('palabras-clave//usuario/', views.gestionar_palabras_clave_usuario, name='gestionar_palabras_usuarios'),
    path('palabras/todas/', views.listar_todas_palabras, name='listar_todas_palabras'),

    # Gestión de Usuarios
    path('usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Gestión de Roles
    path('roles/', views.gestion_roles, name='gestion_roles'),
    path('roles/crear/', views.crear_rol, name='crear_rol'),
    path('roles/editar/<int:id>/', views.editar_rol, name='editar_rol'),
    path('roles/eliminar/<int:id>/', views.eliminar_rol, name='eliminar_rol'),

    #Gestión de Clientes
    path('clientes/', views.gestion_clientes, name='gestion_clientes'),
    path('clientes/subir_excel', views.subir_clientes_excel, name='subir_clientes_excel'),
    path('clientes/descargar-formato/', views.descargar_excel_muestra, name='descargar_excel_muestra'),
    path('clientes/asignar/<int:id>/', views.asignar_cliente_usuario, name='asignar_cliente_usuario'),
    path('clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('mis_clientes/', views.mis_clientes, name='mis_clientes'),
]
