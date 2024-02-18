from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_zip_file(value):
    if not value.name.endswith('.zip'):
        raise ValidationError(_('Archivo debe tener extensión .zip'))
    
def validar_carpeta_docker_compose(maquina):
    # Validar la estructura de la carpeta
    # ...
    pass