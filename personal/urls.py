from django.contrib import admin
from django.urls import path
from . import views
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
    
    path('descargar-archivo/', views.descargar_archivo, name='descargar_archivo'),
    path("prueba/", views.prueba, name='p'),
]