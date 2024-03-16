import re
from django.shortcuts import render,redirect
from gestion.models import *
from django.contrib.auth import logout
#Para gestionar la sesion de la pagina personal, un decorador es algo que permite dar una funcionalidad extra 
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.views import View
from django.conf import settings
#Docker
import docker, subprocess

from django.contrib.auth import update_session_auth_hash #Para cambiar la contraseña y que no se cierre la sesion
from django.contrib.auth.forms import PasswordChangeForm #Para cambiar la contraseña
from personal.forms import FotoPerfilForm # Importo el formulario para cambiar la foto de perfil
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

# Importar módulos para trabajar con correos electrónicos
import imaplib
import email
from email.header import decode_header
from django.contrib.auth.decorators import user_passes_test

#Funciones para gestionar las flags
from personal.functions import submit_user_flag
from django.db.models import Sum # Para sumar la puntuacion total del jugador

#Vista para el inicio de sesion del jugador
@login_required(login_url="inicio")
def personal(request): # Pagina personal del usuario
    p = User.objects.all()
    if request.method == 'GET':
        #Obtengo el nombre del usuario logueado
        jugador= Jugador.objects.get(usuario=request.user)
        maquinas = MaquinaJugador.objects.filter(jugador=jugador)
        context = { 'maquinas': maquinas}
        return render(request, 'gestion/personal.html',context)
    #Gestionar cuando se pulse un boton
    if request.method == 'POST':
         return redirect('inicio')
    
#Hay que pasarle un contexto el cual serán las maquinas que tiene disponible el usuario seleccionado

@login_required(login_url="inicio")
def maquinas(request):
    #Necesito el jugador y las maquinas que tiene disponibles
    if request.method == 'GET':
        #Obtengo las maquinas que tiene disponibles en función de la puntuación del jugador
        jugador= Jugador.objects.get(usuario=request.user)
        maquinas = MaquinaJugador.objects.filter(jugador=jugador)
        # Ordeno las maquinas por orden alfabetico
        maquinas = maquinas.order_by('maquina_vulnerable__nombre')
        context = { 'maquinas': maquinas}
        return render(request, 'personal/maquinas.html',context)
    elif request.method == 'POST': #Si se pulsa el boton de activar o desactivar
        return redirect('maquinas')


def gestionar_maquina(control, usuario, client):
    if control == 1:
        try:	
            client.containers.run(
                image='xxe:maquina1', #Nombre de la imagen de la maquina
                name=usuario,   #Nombre del usuario que la ejeucta
                ports={'80': None}, #Diccionario de los puertos abiertos
                detach=True
            )
        except docker.errors.APIError as e:
            return HttpResponse(f'Error al crear el contenedor: {e}')
    elif control == 2:
        try:
            existing_container = client.containers.get(usuario)
            existing_container.stop()
            existing_container.remove()
        except docker.errors.NotFound:
            pass
    else:
        #Reiniciar contenedor
        print("HOla")

#Vista previa de la maquina seleccionada
@login_required(login_url="inicio")
def gestion_maquina(request, nombre_maquina):
    #A partir de nombre_maquina-> la maquina MaquinaDocker, MaquinaDockerCompose o MaquinaVirtual
    #Obtener la relacion entre el jugador y la maquina
    relacion_maquina_jugador= MaquinaJugador.objects.get(maquina_vulnerable=MaquinaVulnerable.objects.get(nombre=nombre_maquina), jugador=Jugador.objects.get(usuario=request.user))
    # Intentar buscar en MaquinaDockerCompose
    maquina_compose = MaquinaDockerCompose.objects.filter(nombre=nombre_maquina).first()
    conseguido = PuntuacionJugador.objects.filter(jugador=Jugador.objects.get(usuario=request.user), maquina_vulnerable=relacion_maquina_jugador.maquina_vulnerable, bandera=0).first()
    conseguido1 = PuntuacionJugador.objects.filter(jugador=Jugador.objects.get(usuario=request.user), maquina_vulnerable=relacion_maquina_jugador.maquina_vulnerable, bandera=1).first()
    if maquina_compose:
        pass
    else:
        # Si no es MaquinaDockerCompose, buscar en MaquinaDocker
        maquina_docker = MaquinaDocker.objects.filter(nombre=nombre_maquina).first()
        if maquina_docker:
            pass
        else:
            # Si no es MaquinaDocker ni MaquinaDockerCompose, buscar en MaquinaVirtual
            maquina_virtual = MaquinaVirtual.objects.filter(nombre=nombre_maquina).first()
            if maquina_virtual:
               pass
            else:
                # Si no es ninguno de los anteriores
                pass
    context={'relacion_maquina_jugador':relacion_maquina_jugador, 'conseguido': conseguido, 'conseguido1': conseguido1, 'control': None}
    return render(request, 'personal/maquinaSeleccionada.html',context)

#Para poder activarse el metodo debe de ser post y además ninguna maquina del usuario tiene que estar activa
@login_required(login_url="inicio")
def activar_maquina(request, nombre_maquina):
    if request.method == 'POST': 
        jugador = Jugador.objects.get(usuario=request.user)
        maquina = MaquinaVulnerable.objects.get(nombre=nombre_maquina)
        relacion_maquina_jugador = MaquinaJugador.objects.get(jugador=jugador, maquina_vulnerable=maquina)
        if relacion_maquina_jugador.activa:
            messages.warning(request, 'La máquina ya está activa.')
            return redirect('gestion_maquina' , nombre_maquina)
        else:
            for maquina_jugadoR in MaquinaJugador.objects.filter(jugador=jugador):
                if maquina_jugadoR.activa:
                    messages.error(request, 'Ya hay una maquina activa')
                    #Redirigir a la vista gestion_maquina con una variable que indique que ya hay una maquina activa
                    return redirect('gestion_maquina' , nombre_maquina)
            # Una vez llega aqui la maquina NO debería de estar activada por lo que se comprueba de qué tipo de la maquina vulnerable es
            if not jugador_conectado_vpn(jugador.usuario.username):
                messages.error(request, "Por favor conectese primero al servidor VPN")
            else:
                relacion= MaquinaJugador.objects.get(maquina_vulnerable=MaquinaVulnerable.objects.get(nombre=nombre_maquina), jugador=Jugador.objects.get(usuario=request.user))
                if hasattr(maquina, 'maquinadocker'):
                    relacion_maquina_jugador.activa = True
                    relacion_maquina_jugador.save()
                    if not relacion_maquina_jugador.activa:
                        messages.error(request, 'Error al levantar la maquina.')
                elif hasattr(maquina, 'maquinadockercompose'):
                    relacion_maquina_jugador.activa = True
                    relacion_maquina_jugador.save()
                    if not relacion_maquina_jugador.activa:
                        messages.error(request, 'Error al levantar la maquina.')
                elif hasattr(maquina, 'maquinavirtual'):
                    messages.success(request, 'La máquina es de tipo OtroTipoDeMaquina.')
                #Ejecutar la funcion de iptables para eliminar la regla correspondiente
            
            return redirect('gestion_maquina', nombre_maquina=nombre_maquina)
    else:
        #Redirige a la pagina anterior si no es un metodo post
        return redirect('maquinas')

    
@login_required(login_url="inicio")
def desactivar_maquina(request, nombre_maquina):
    if request.method == 'POST':
        jugador = Jugador.objects.get(usuario=request.user)
        maquina = MaquinaVulnerable.objects.get(nombre=nombre_maquina)
        maquina_jugador = MaquinaJugador.objects.get(jugador=jugador, maquina_vulnerable=maquina)
        
        if not maquina_jugador.activa:
            messages.warning(request, 'La máquina ya está desactivada.')
        else:
            if hasattr(maquina, 'maquinadocker'):
                maquina_jugador.activa = False
                maquina_jugador.save()
            elif hasattr(maquina, 'maquinadockercompose'):
                maquina_jugador.activa = False
                maquina_jugador.save()
            elif hasattr(maquina, 'maquinavirtual'):
                messages.success(request, 'La máquina es de tipo MaquinaVirtual.')
        return redirect('gestion_maquina', nombre_maquina=nombre_maquina)
    else:
        return redirect('maquinas')

@login_required(login_url="inicio")
def descargar_archivo(request):
    nombre_archivo = request.user.username + ".ovpn"
    # Construir la ruta completa al archivo
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, "vpns/" + nombre_archivo)
    messages.warning(request, 'La ruta es: ' + ruta_archivo)
    # Verificar si el archivo existe
    if os.path.exists(ruta_archivo):
        # Abrir el archivo para lectura binaria
        with open(ruta_archivo, 'rb') as archivo:
            # Crear una respuesta HTTP con el contenido del archivo
            response = HttpResponse(archivo.read(), content_type='application/force-download')
            
            # Establecer el encabezado Content-Disposition para forzar la descarga
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            
            return response
    else:
        return HttpResponse("El archivo no fue encontrado.", status=404)

def logout_vista(request):
    #Cerrar sesión mediante get sin que me de fallo
    logout(request)
    return redirect('inicio')

@login_required(login_url="inicio")
def profile(request):
    if request.method == 'POST':
        # Procesar el formulario de cambio de contraseña
        formPassword = PasswordChangeForm(request.user, request.POST)
        formImage = FotoPerfilForm(request.POST, request.FILES, instance=request.user.jugador)
        if formPassword.is_valid():
            user = formPassword.save()
            # Después de cambiar la contraseña, realiza el relogin del usuario
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada con éxito.')
            return redirect('profile')  # Redirige a la página del perfil o a donde desees

        # Procesar el formulario de cambio de imagen de perfil
        elif formImage.is_valid():
            if formImage.cleaned_data.get('submit_button') == 'photo_submit':
                # Obtengo el nombre de la imagen
                formImage.save()
                messages.success(request, 'Foto de perfil cambiada con éxito.')
                return redirect('profile')
        else:
            # Se modifican los datos personales del usuario
            user = request.user
            user.first_name = request.POST.get('nombre')
            user.last_name = request.POST.get('apellidos')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Datos personales cambiados con éxito.')
            return redirect('profile')

    else:
        formPassword = PasswordChangeForm(request.user)
        formImage = FotoPerfilForm(instance=request.user.jugador)

    return render(request, 'personal/perfil.html', {'formPassword': formPassword, 'formImage': formImage})

# Ver perfil de usuario seleccionado
@login_required(login_url="inicio")
def ver_perfil(request, jugador_id):
    jugador = get_object_or_404(Jugador, pk=jugador_id) #if jugador.usuario != request.user
    return render(request, 'personal/perfil_jugador.html', {'jugador': jugador})


# Vistas para gestionar las flags
@login_required(login_url="inicio")
def flag(request, nombre_maquina):
    # Obtengo por POST la flag si es flag1 o flag2
    flag = request.POST.get('flag1')
    flag2 = request.POST.get('flag2')
    maquina = MaquinaVulnerable.objects.get(nombre=nombre_maquina)
    jugador = Jugador.objects.get(usuario=request.user)
    if flag:
        # Compruebo que el usuario no haya conseguido ya esa flag
        if PuntuacionJugador.objects.filter(jugador=jugador, maquina_vulnerable=maquina, bandera=0).first():
            messages.error(request, 'Ya has conseguido esa flag')
            return redirect('gestion_maquina', nombre_maquina=nombre_maquina)
    # Compruebo que la flag sea igual a la flag de la maquina
        if maquina.bandera_usuario_inicial == flag:
            # Cambio el estado de la flag, añado la puntuación al jugador y cambio el estado de la máquina a apagado
            # (si es necesario, es decir si se han completado todas las flags)
            control = 1
            submit_user_flag(jugador, maquina, 0)
        else:
            control = 2
            messages.error(request, 'Flag incorrecta')
    elif flag2:
        # Compruebo que el usuario no haya conseguido ya esa flag
        if PuntuacionJugador.objects.filter(jugador=jugador, maquina_vulnerable=maquina, bandera=1).first():
            messages.error(request, 'Ya has conseguido esa flag')
            return redirect('gestion_maquina', nombre_maquina=nombre_maquina)
        if maquina.bandera_usuario_root == flag2:
            control = 1
            submit_user_flag(jugador, maquina, 1)
            # Cambio el estado de la flag, añado la puntuación al jugador y cambio el estado de la máquina a apagado
            # (si es necesario, es decir si se han completado todas las flags)
        else:
            control = 2
            messages.error(request, 'Flag incorrecta')
    else:
        control = 2
    conseguido = PuntuacionJugador.objects.filter(jugador=jugador, maquina_vulnerable=maquina, bandera=0).first()
    conseguido1 = PuntuacionJugador.objects.filter(jugador=jugador, maquina_vulnerable=maquina, bandera=1).first()
    relacion_maquina_jugador = MaquinaJugador.objects.get(jugador=jugador, maquina_vulnerable=maquina)
    print(control)
    #return redirect('gestion_maquina', nombre_maquina=nombre_maquina)
    return render(request, 'personal/maquinaSeleccionada.html', {'relacion_maquina_jugador': relacion_maquina_jugador, 'conseguido': conseguido, 'conseguido1': conseguido1, 'control': control})

# Ranking
@login_required(login_url="inicio")
def ranking(request):
    # Obtengo el ranking de los jugadores
    jugadores = Jugador.objects.all().order_by('-puntuacion')
    return render(request, 'personal/ranking.html', {'jugadores': jugadores})
# Vista para ver los ultimos 10 correos tiene que ser usuario admin
def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def get_last_10_emails(request):
    # Datos del servidor
    username = "marpagamarco@gmail.com"
    password = "wpqdzopxecragcyq"
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)

    # Selecciona la bandeja de entrada (inbox)
    mail.select("inbox")

    # Busca los últimos correos electrónicos (en este caso, los 5 más recientes)
    status, messages = mail.search(None, 'UNSEEN')
    mail_ids = messages[0].split()

    correos = []
    for i in range(max(0, len(mail_ids)-5), len(mail_ids)):
        status, msg_data = mail.fetch(mail_ids[i], '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                email_message = email.message_from_bytes(response_part[1])

                # Procesa la información del correo electrónico según tus necesidades
                subject, encoding = decode_header(email_message["Subject"])[0]
                subject = subject.decode(encoding) if encoding else subject
                from_address = email.utils.parseaddr(email_message.get("From"))[1]

                # Obtén el contenido del mensaje
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            content = part.get_payload(decode=True).decode("utf-8")
                            break
                else:
                    content = email_message.get_payload(decode=True).decode("utf-8")

                # Agrega detalles del correo a la lista
                correos.append({
                    "from_address": from_address,
                    "subject": subject,
                    "content": content
                })
    # Si no hay correos no leidos muestra los 5 ultimos correos
    if len(correos) == 0:
        status, messages = mail.search(None, 'ALL')
        mail_ids = messages[0].split()
        for i in range(max(0, len(mail_ids)-5), len(mail_ids)):
            status, msg_data = mail.fetch(mail_ids[i], '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    email_message = email.message_from_bytes(response_part[1])

                    # Procesa la información del correo electrónico según tus necesidades
                    subject, encoding = decode_header(email_message["Subject"])[0]
                    subject = subject.decode(encoding) if encoding else subject
                    from_address = email.utils.parseaddr(email_message.get("From"))[1]

                    # Obten el contenido del mensaje
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                content = part.get_payload(decode=True).decode("utf-8")
                                break
                    else:
                        content = email_message.get_payload(decode=True).decode("utf-8")

                    # Agrega detalles del correo a la lista
                    correos.append({
                        "from_address": from_address,
                        "subject": subject,
                        "content": content
                    })
                    
    # Cierra la conexión
    mail.logout()
    correos.reverse()
    return render(request, 'personal/prueba.html',{'correos': correos})


#Comprobar si se puede conseguir una instancia de docker
def listaContDocker(request):
    client = docker.from_env()
    containers = client.containers.list()

    container_info = ""
    for container in containers:
        container_info += f"Nombre: {container.name}, ID: {container.id}\n"

    return HttpResponse("Información de contenedores:\n" + container_info)
