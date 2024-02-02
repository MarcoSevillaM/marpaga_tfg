from django.contrib import admin
from .models import *

#admin.site.register(MaquinaJugador)

class VerMaquinaVulnerable(admin.ModelAdmin):
    list_display = ('nombre', 'nivel_dificultad','nivel_minimo_activacion')  # Campos que se mostrarán en la lista
    list_filter = ('nivel_dificultad','nivel_minimo_activacion')  # Campos por los cuales se pueden filtrar

class VerJugadores(admin.ModelAdmin):
    list_display = ('usuario', 'nivel','puntuacion')  # Campos que se mostrarán en la lista
    list_filter = ('nivel'),  # Campos por los cuales se pueden filtrar

class VerRelacionJugadorMaquina(admin.ModelAdmin):
    list_display = ('jugador', 'maquina_vulnerable','activa')  # Campos que se mostrarán en la lista

    list_filter = ('maquina_vulnerable', 'jugador')  # Campos por los cuales se pueden filtrar

admin.site.register(MaquinaVulnerable, VerMaquinaVulnerable)
admin.site.register(Jugador, VerJugadores)
admin.site.register(MaquinaJugador, VerRelacionJugadorMaquina)

# Maquinas soportadas en el sistema
# Maquinas Docker a partir de un Dockerfile
@admin.register(MaquinaDocker)
class MaquinaDockerAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nivel_dificultad', 'nivel_minimo_activacion', 'imagen_docker', 'puerto_exposicion']

# Maquinas Docker generadas con un Docker Compose
@admin.register(MaquinaDockerCompose)
class MaquinaDockerComposeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nivel_dificultad', 'nivel_minimo_activacion', 'archivo']

# Maquinas Virtuales 
@admin.register(MaquinaVirtual)
class MaquinaVirtualAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nivel_dificultad', 'nivel_minimo_activacion']



