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
    comando = f"docker run --name {jugador.usuario.username} -d --rm {nombre_maquina}"
    print(comando)
    try:
        subprocess.run(comando, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al levantar el contenedor: {e}")
        return False

# Funciones para levantar y bajar docker-compose
