from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import subprocess
def Validate_zip_file(value):
    if not value.name.endswith('.zip'):
        raise ValidationError(_('Archivo debe tener extensión .zip'))
    
def Validar_carpeta_docker_compose(maquina):
    # Validar la estructura de la carpeta
    # ...
    pass

class OverwriteStorage(FileSystemStorage):
    def Get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

# Funciones para levantar y bajar contenedores docker
def Up_docker_machine(maquina, jugador):
    nombre_maquina = maquina.nombre
    ruta_dockerfile = f'maquinas_docker/{nombre_maquina}/Dockerfile'
    comando = f"docker run --name {jugador.usuario.username} -d --rm {nombre_maquina.lower()}"
    print(comando)
    try:
        subprocess.run(comando, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al levantar el contenedor: {e}")
        return False

# Funciones para levantar y bajar docker-compose




# Disparadores
def crear_jugador_al_crear_usuario(sender, instance, created, **kwargs):
    if created:
        jugador = Jugador.objects.create(usuario=instance) #Crea el jugador
        maquinas_disponibles = MaquinaVulnerable.objects.all()
        for maquina in maquinas_disponibles:
            if jugador.puntuacion >= maquina.puntuacion_minima_activacion:
                MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=maquina)

#Crear relaciones con los jugadores cuando se crea una maquina Docker Compose
def crear_relacion_al_crear_maquina_docker_compose(sender, instance, created, **kwargs):
    if created:
        jugadores = Jugador.objects.all()
        for jugador in jugadores:
            if jugador.puntuacion >= instance.puntuacion_minima_activacion:
                MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=instance)

# Función para crear la realción maquina-jugador cuando se actualiza la puntuación de un jugador
def crear_relacion_al_actualizar_puntuacion(sender, instance, **kwargs):
    maquinas_disponibles = MaquinaVulnerable.objects.all()
    jugador = Jugador.objects.get(usuario=instance.usuario)
    for maquina in maquinas_disponibles:
        # Obtener el jugador
        if jugador.puntuacion >= maquina.puntuacion_minima_activacion:
            MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=maquina)

