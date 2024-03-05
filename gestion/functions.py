from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
def validate_zip_file(value):
    if not value.name.endswith('.zip'):
        raise ValidationError(_('Archivo debe tener extensión .zip'))
    
def validar_carpeta_docker_compose(maquina):
    # Validar la estructura de la carpeta
    # ...
    pass

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name