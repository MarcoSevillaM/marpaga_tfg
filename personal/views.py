from django.shortcuts import render,redirect, reverse
from gestion.models import *

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
def gestion_maquina(request, nombre_maquina):
    #A partir de nombre_maquina-> la maquina MaquinaDocker, MaquinaDockerCompose o MaquinaVirtual
    #Obtener la relacion entre el jugador y la maquina
    relacion= MaquinaJugador.objects.get(maquina_vulnerable=MaquinaVulnerable.objects.get(nombre=nombre_maquina), jugador=Jugador.objects.get(usuario=request.user))
    maquina=relacion.maquina_vulnerable
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
    context={'relacion':relacion, 'variable':variable}
    return render(request, 'personal/maquinaSeleccionada.html',context)

#Para poder activarse el metodo debe de ser post y además ninguna maquina del usuario tiene que estar activa
def activar_maquina(request, nombre_maquina):
    if request.method == 'POST': 
        jugador = Jugador.objects.get(usuario=request.user)
        maquina = MaquinaVulnerable.objects.get(nombre=nombre_maquina)
        maquina_jugador = MaquinaJugador.objects.get(jugador=jugador, maquina_vulnerable=maquina)
        if maquina_jugador.activa:
            messages.warning(request, 'La máquina ya está activa.')
            return redirect('gestion_maquina' , nombre_maquina)
        else:
            for maquina_jugadoR in MaquinaJugador.objects.filter(jugador=jugador):
                if maquina_jugadoR.activa:
                    messages.warning(request, 'Ya hay una maquina activa')
                    return redirect('gestion_maquina' , nombre_maquina)
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
                    maquina_jugador.activa = True
                    maquina_jugador.save()
                    messages.success(request, f'Máquina activada exitosamente,{ maquina_jugador.maquina_vulnerable.nombre}')
            elif hasattr(maquina, 'maquinadockercompose'):
                messages.success(request, 'La máquina es de tipo MaquinaDockerCompose.')
                ruta_docker_compose = f'maquinas_docker_compose/{maquina.nombre}/docker-compose.yml'
                comando = f"docker-compose -f {ruta_docker_compose} up -d"  
                subprocess.run(comando, shell=True, check=True)
                #Obtengo la direccion de la maquina
                direccion = subprocess.run("docker exec startrek-payroll-nginx ifconfig eth0 | awk '/inet / {print $2}'", shell=True, check=True, capture_output=True)
                maquina_jugador.activa = True
                maquina_jugador.save()
                messages.success(request, 'La dirección de la máquina es: ' + direccion.stdout.decode('utf-8'))
            elif hasattr(maquina, 'maquinavirtual'):
                messages.success(request, 'La máquina es de tipo OtroTipoDeMaquina.')
            #return render(request, template_name='gestion_maquina', {'nombre_maquina':nombre_maquina, 'context':context})
            #return render(request, 'gestion/gestion_maquina.html' , context={'nombre_maquina': nombre_maquina, 'relacion':relacion, 'variable':direccion})
            #return redirect(reverse='gestion_maquina', kwargs={'nombre_maquina':nombre_maquina, 'direccion':direccion.stdout.decode('utf-8')})
            #return redirect('gestion_maquina' nombre_maquina, 'direccion': direccion.stdout.decode('utf-8')))
            return(reverse('gestion_maquina', 'nombre_maquina': nombre_maquina))
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
            elif hasattr(maquina, 'maquinadockercompose'):
                messages.success(request, 'La máquina es de tipo MaquinaDockerCompose.')
                ruta_docker_compose = f'maquinas_docker_compose/{maquina.nombre}/'
                #ruta_docker_compose = "/home/marco/Escritorio/TFG/marpaga_tfg/maquinas_docker_compose/startrek_payroll/Makefile"
                comando = f"make -C {ruta_docker_compose} clean"
                print(comando)
                print("-----------------------------------------------------------------------")
                print(subprocess.run(comando, shell=True, check=True))
                print("-----------------------------------------------------------------------")
                #subprocess.run(comando, shell=True, check=True)
                maquina_jugador.activa = False
                maquina_jugador.save()
                return redirect('gestion_maquina', nombre_maquina=nombre_maquina)
            elif hasattr(maquina, 'maquinavirtual'):
                messages.success(request, 'La máquina es de tipo MaquinaVirtual.')
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
#Comprobar si se puede conseguir una instancia de docker
def prueba(request):
    client = docker.from_env()
    containers = client.containers.list()

    container_info = ""
    for container in containers:
        container_info += f"Nombre: {container.name}, ID: {container.id}\n"

    return HttpResponse("Información de contenedores:\n" + container_info)
 #   return FileResponse(model.image.open(), as_attachment=True)
