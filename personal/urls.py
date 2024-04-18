from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import PasswordChangeView
urlpatterns = [
    # Pagina principal del usuario, donde se muestra su nombre, su nivel, su puntuacion, su foto de perfil,
    # un boton para acceder a las maquinas disponibles, un boton de enlace de descarga de la VPN, un boton para cambiar la contraseña y un boton para cerrar sesion.
    path("", views.personal, name='personal'),
    # Listado de las maquinas disponibles y un enlace para acceder a cada una de ellas 
    path("maquinas/", views.maquinas, name='maquinas'), 

    # Pagina de gestion de la maquina seleccionada, donde se muestra el nombre de la maquina, su nivel de dificultad, su estado (activa o inactiva),
    # un boton para activarla y otro para desactivarla, además de informacion sobre la maquina y unas etiquetas para introducir las banderas.
    path("maquinas/<str:nombre_maquina>/", views.gestion_maquina, name='gestion_maquina'),

    # Direccion para activar una maquina
    path("maquinas/<str:nombre_maquina>/activar/", views.activar_maquina, name='activar_maquina'),

    # Direccion para desactivar una maquina
    path("maquinas/<str:nombre_maquina>/desactivar/", views.desactivar_maquina, name='desactivar_maquina'),
    path("logout_vista", views.logout_vista, name='logout_vista'),
    
    path('descargar-archivo/', views.descargar_archivo, name='descargar_archivo'), # Vista para descargar el archivo.ovpn

    path('profile/', views.profile, name='profile'), # Vista para cambiar datos del perfil
    path('profile/<int:jugador_id>/', views.ver_perfil, name='profile_jugador'), # Vista para ver el perfil del jugador
    # Vistas para gestionar las flags
    path('flag/<str:nombre_maquina>', views.flag, name='flag'),
    
    # Ranking
    path('ranking/', views.ranking, name='ranking'),
    # Logros personales
    path('logros/', views.logros, name='logros'),
    # Valorar una bandera de una detemina maquina
    path('ranking/guardar_valoracion/', views.valoracion, name='guardar_valoracion'),
    # Ver los ultimos 10 correos recibidos
    path("correos/", views.get_last_10_emails, name='correos'),

    # Despurar docker
    path('listaContDocker/', views.listaContDocker, name='listaContDocker'),
]