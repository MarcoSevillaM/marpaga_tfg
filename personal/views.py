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

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
def prueba(request):
    context = {}
    return render(request, 'gestion/personal.html', context)

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
        #Obtengo el nombre del usuario logueado
        jugador= Jugador.objects.get(usuario=request.user)
        maquinas = MaquinaJugador.objects.filter(jugador=jugador)
        
        context = { 'maquinas': maquinas,}
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
    if maquina_compose:
        variable = "Es una maquina Docker Compose"
    else:
        # Si no es MaquinaDockerCompose, buscar en MaquinaDocker
        maquina_docker = MaquinaDocker.objects.filter(nombre=nombre_maquina).first()
        if maquina_docker:
            variable = "Es una maquina Docker"
        else:
            # Si no es MaquinaDocker ni MaquinaDockerCompose, buscar en MaquinaVirtual
            maquina_virtual = MaquinaVirtual.objects.filter(nombre=nombre_maquina).first()
            if maquina_virtual:
                variable = "Es una maquina Virtual"
            else:
                # Si no es ninguno de los anteriores
                variable = "Es una maquinaaaa"
    context={'relacion_maquina_jugador':relacion_maquina_jugador, 'variable':variable}
    return render(request, 'personal/maquinaSeleccionada.html',context)

#Para poder activarse el metodo debe de ser post y además ninguna maquina del usuario tiene que estar activa
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
                    messages.warning(request, 'Ya hay una maquina activa')
                    print("Ya hay una maquina activa")
                    #Redirigir a la vista gestion_maquina con una variable que indique que ya hay una maquina activa
                    return redirect('gestion_maquina' , nombre_maquina)
                    #return redirect('gestion_maquina' , nombre_maquina)
            # Una vez llega aqui la maquina NO debería de estar activada por lo que se comprueba de qué tipo de la maquina vulnerables
            relacion= MaquinaJugador.objects.get(maquina_vulnerable=MaquinaVulnerable.objects.get(nombre=nombre_maquina), jugador=Jugador.objects.get(usuario=request.user))
            if hasattr(maquina, 'maquinadocker'):
                messages.success(request, 'La máquina es de tipo MaquinaDocker.')
                client = docker.from_env()
                try:
                    client.containers.get(jugador.usuario.username) # Si esto da error significa que el usuario no tiene ninguna maquina en docker activa
                    messages.warning(request, 'Ya hay una máquina activa en Docker.')
                    return redirect('maquinas')
                except docker.errors.NotFound:
                    #gestionar_maquina(1, jugador.usuario.username, client) # Activar la máquina
                    relacion_maquina_jugador.activa = True
                    relacion_maquina_jugador.save()
                    messages.success(request, f'Máquina activada exitosamente,{ relacion_maquina_jugador.maquina_vulnerable.nombre}')
            elif hasattr(maquina, 'maquinadockercompose'):
                relacion_maquina_jugador.activa = True
                relacion_maquina_jugador.save()
            elif hasattr(maquina, 'maquinavirtual'):
                messages.success(request, 'La máquina es de tipo OtroTipoDeMaquina.')
            #Ejecutar la funcion de iptables para eliminar la regla correspondiente
            
            return redirect('gestion_maquina', nombre_maquina=nombre_maquina)
    else:
        #Redirige a la pagina anterior si no es un metodo post
        return redirect('maquinas')

    

def desactivar_maquina(request, nombre_maquina):
    if request.method == 'POST':
        jugador = Jugador.objects.get(usuario=request.user)
        maquina = MaquinaVulnerable.objects.get(nombre=nombre_maquina)
        maquina_jugador = MaquinaJugador.objects.get(jugador=jugador, maquina_vulnerable=maquina)
        
        if not maquina_jugador.activa:
            messages.warning(request, 'La máquina ya está desactivada.')
        else:
            if hasattr(maquina, 'maquinadocker'):
                messages.success(request, 'La máquina es de tipo MaquinaDocker.')
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

#Comprobar si se puede conseguir una instancia de docker
def prueba(request):
    client = docker.from_env()
    containers = client.containers.list()

    container_info = ""
    for container in containers:
        container_info += f"Nombre: {container.name}, ID: {container.id}\n"

    return HttpResponse("Información de contenedores:\n" + container_info)
 #   return FileResponse(model.image.open(), as_attachment=True)
