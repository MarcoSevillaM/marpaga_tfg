from gestion.models import PuntuacionJugador
from django.utils import timezone

# Función para añadir que un usuario ha resuelto un reto
def  submit_user_flag(usuario, maquina, flag):
    # Cuando el usuario entra aqui ya se ha comprobado que la flag es correcta
    puntuacion = 100
    fecha_obtencion = timezone.now()
    nuevo = PuntuacionJugador(jugador=usuario, maquina_vulnerable=maquina, puntuacion=puntuacion, fecha_obtencion=fecha_obtencion, bandera=flag)
    nuevo.save()
