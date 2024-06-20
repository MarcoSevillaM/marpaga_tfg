from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import subprocess
import time

def Validate_zip_file(value):
    """
    Función que valida que el archivo sea un archivo .zip
    """
    #Comprobará que el fichero termine en .zip o directamente que se quiera conservar el nombre del fichero anterior
    if not value and not os.path.isfile(value.path):
        return
    elif not value.name.endswith('.zip'):
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

