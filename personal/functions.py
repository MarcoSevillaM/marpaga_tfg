from gestion.models import PuntuacionJugador
from django.utils import timezone

# Función para añadir que un usuario ha resuelto un reto
def  submit_user_flag(usuario, maquina, flag):
    # Cuando el usuario entra aqui ya se ha comprobado que la flag es correcta
    # Para asignar puntuaciones a problemas de dificultad fácil, podrías establecer un rango de puntuaciones adecuado para ese nivel. Por ejemplo, podrías asignar una puntuación máxima de \(P_{\text{max\_fácil}}\) a los problemas de dificultad fácil. La fórmula podría ser similar a la mencionada anteriormente:
    # \[ \text{Puntuación} = D \times (\text{Resultado A} + k \times \text{Resultado B}) \]
    # Para dificultad fácil, podrías ajustar \(D\) a valores más bajos (por ejemplo, entre 1 y 3, dependiendo de tu escala) y asignar una puntuación máxima de \(P_{\text{max\_fácil}}\).
    # El objetivo es que los problemas más fáciles tengan puntuaciones más bajas en comparación con los problemas de mayor dificultad. Ajusta los parámetros según tus preferencias y el rango que desees asignar a los problemas de dificultad fácil.
    # Por ello la puntuación maxima para problemas de dificultad fácil será 100, y para problemas de dificultad media 200, y para problemas de dificultad dificil 300
    dificultad = maquina.nivel_dificultad
    print("Dificultad: ", dificultad)
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
    print("Puntuacion: ", puntuacion)
    fecha_obtencion = timezone.now()
    nuevo = PuntuacionJugador(jugador=usuario, maquina_vulnerable=maquina, puntuacion=puntuacion, fecha_obtencion=fecha_obtencion, bandera=flag)
    usuario.puntuacion += puntuacion
    usuario.save()
    nuevo.save()
