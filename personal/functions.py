from gestion.models import PuntuacionJugador
from django.utils import timezone

# Función para añadir que un usuario ha resuelto un reto
def  submit_user_flag(usuario, maquina, flag):
    # Cuando el usuario entra aqui ya se ha comprobado que la flag es correcta
    # Por ello la puntuación maxima para problemas de dificultad fácil será 100, y para problemas de dificultad media 200, y para problemas de dificultad dificil 300
    dificultad = maquina.nivel_dificultad
    # Ahora veo si el jugador ha introducido la bandera del usuario o la del root
    if not flag:
        if dificultad.lower() == "facil":
            puntuacion = 100 * 0.6
        elif dificultad.lower() == "media":
            puntuacion = 200 * 0.5
        elif dificultad.lower() == "difcil":
            puntuacion = 300 * 0.4
        elif dificultad.lower() == "experta":
            puntuacion = 400 * 0.3
        else:
            puntuacion = 0
    else:
        if dificultad.lower() == "facil":
            puntuacion = 100 * 0.4
        elif dificultad.lower() == "media":
            puntuacion = 200 * 0.5
        elif dificultad.lower() == "difcil":
            puntuacion = 300 * 0.6
        elif dificultad.lower() == "experta":
            puntuacion = 400 * 0.7
        else:
            puntuacion = 0
    fecha_obtencion = timezone.now()
    nuevo = PuntuacionJugador(jugador=usuario, maquina_vulnerable=maquina, puntuacion=puntuacion, fecha_obtencion=fecha_obtencion, bandera=flag)
    nuevo.save()
    return puntuacion
