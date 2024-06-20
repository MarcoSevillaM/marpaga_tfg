from django.contrib import admin
from .models import *

#admin.site.register(MaquinaJugador)
admin.site.register(PuntuacionJugador)

class VerMaquinaVulnerable(admin.ModelAdmin):
    """
    Clase que muestra las máquinas vulnerables en el panel de administración, así como sus filtros y columnas deseadas
    """
    list_display = ('nombre', 'nivel_dificultad','puntuacion_minima_activacion')  # Campos que se mostrarán en la lista
    list_filter = ('nivel_dificultad','puntuacion_minima_activacion')  # Campos por los cuales se pueden filtrar

class VerJugadores(admin.ModelAdmin):
    """
    Clase que muestra los jugadores en el panel de administración, así como sus filtros y columnas deseadas
    """
    list_display = ('usuario', 'obtener_puntuacion')  # Campos que se mostrarán en la lista

    def obtener_puntuacion(self, obj):
        """
        Función que obtiene la puntuación de un jugador

        Args:
            obj (Jugador): El objeto jugador

        Returns:
            int: La puntuación del jugador
        """
        return obj.puntuacion

    obtener_puntuacion.short_description = 'Puntuación'

class VerRelacionJugadorMaquina(admin.ModelAdmin):
    """
    Clase que muestra la relación entre jugadores y máquinas vulnerables en el panel de administración, así como sus filtros y columnas deseadas
    """
    list_display = ('jugador', 'maquina_vulnerable','activa', 'ip_address')  # Campos que se mostrarán en la lista

    list_filter = ('maquina_vulnerable', 'activa')  # Campos por los cuales se pueden filtrar

admin.site.register(MaquinaVulnerable, VerMaquinaVulnerable)
admin.site.register(Jugador, VerJugadores)
admin.site.register(MaquinaJugador, VerRelacionJugadorMaquina)
admin.site.register(ValoracionJugador)
# Maquinas soportadas en el sistema
# Maquinas Docker a partir de un Dockerfile
@admin.register(MaquinaDocker)
class MaquinaDockerAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nivel_dificultad', 'puntuacion_minima_activacion', 'archivo']

# Maquinas Docker generadas con un Docker Compose
@admin.register(MaquinaDockerCompose)
class MaquinaDockerComposeAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nivel_dificultad', 'puntuacion_minima_activacion', 'archivo']

# Maquinas Virtuales 
@admin.register(MaquinaVirtual)
class MaquinaVirtualAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nivel_dificultad', 'puntuacion_minima_activacion']
