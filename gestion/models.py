import zipfile
import os
import secrets
import subprocess
import re
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .functions import OverwriteStorage, Validate_zip_file, Validar_carpeta_docker_compose
from django.db.models.signals import pre_delete
from django.contrib import messages
import shutil
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum
import threading
'''
    NOTAS IMPORTANTES
    - Cuando un usuario avance de nivel habrá que crear más tablas en la tabla de relaciones maquinas con jugadores
'''
"""
La base de datos inicialmente estará formada por:
1.Usuarios:
    1.1 Nombre de usuario (clave)
    1.2 Correo electronico (inicialmente en blanco->luego obligatorio ya que será para verificar el correo)
    1.3 Nombre (Puede ir en blanco)
    1.4 Apellido (Puede ir en blanco)
    1.5 Contraseña (obligatorio)
2. Jugador:
    2.1 Nombre del usuario
    2.2 Nivel inicial:0 (Cuando se alacance la experiencia suficiente se subirá de nivel y la experiencia se pondrá a 0 y será oculto al sistema)
    2.3 Puntuacion:Usada para subir el nivel (Inicialmente a 0 y será oculta)
    2.4 (Buscar la manera de enlazar las maquinas con el perfil de tal manera, saber las maquinas que se han valorado, vulnerado y que estan activas o desactivadas)
3. Maquinas vulnerables:
    3.1 Nombre de la maquina
    3.2 Nivel de dificultad (para otorgar la puntuación)
    3.3 Nivel minimo para que el jugador pueda activarla
    3.4 Bandera del usuario inicial
    3.5 Bandera del usuario root
4. Puntuación:
    4.1 Puntuación del jugador
    4.2 Nivel del jugador
    4.3 Experiencia del jugador
"""
#Para los disparadores que cuando se crea un usario se crea un jugador
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver

# # La base de datos contendrá unos usuarios denominados "jugadores" con su perfil propio
class Jugador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(default=0) #Se usará para el ranking y dependerá de las banderas obtenidas en cada maquina, su dificultad y tiempo en conseguirlo.
    foto_perfil = models.ImageField(upload_to='photoPersonal/', blank=True, null=True, storage=OverwriteStorage(), default='photoPersonal/default.jpg')
    
    # Cuando se crea un jugador se le crea un cliente vpn por lo que se ejecuta el script createUserVPN.sh
    def save(self, *args, **kwargs):
        if self.pk is None: # Si es un nuevo usuario
            super().save(*args, **kwargs)
            # Ejecutar el script para crear el usuario VPN
            comando = f"sudo ./createUserVPN.sh add {self.usuario.username}"
            subprocess.run(comando, shell=True, check=True)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.usuario.username
    class Meta: 
        verbose_name_plural="Jugadores"
    def obtener_puntuacion(self):
        return PuntuacionJugador.objects.filter(jugador=self).aggregate(Sum('puntuacion'))['puntuacion__sum']

class MaquinaVulnerable(models.Model):
    DIFFICULT_CHOICES = (
        ('Facil', 'Facil'),
        ('Media', 'Media'),
        ('Dificil', 'Dificil'),
        ('Experta', 'Experta'),
    )
    nombre = models.CharField(max_length=255)
    nivel_dificultad = models.CharField(max_length=10, choices=DIFFICULT_CHOICES)
    puntuacion_minima_activacion = models.IntegerField(default=0)
    descripcion = models.TextField(max_length=255, blank=True, null=True) # Descripcion de la maquina
    # Bandera del usuario inicial y root
    bandera_usuario_inicial = models.CharField(max_length=25, default=secrets.token_hex(12)) #Tendrá que coincidir con la bandera del usuario en la maquina
    bandera_usuario_root = models.CharField(max_length=25, default=secrets.token_hex(12)) #Tendrá que coincidicir con la bandera del root rn la maquina
    # Intrucciones para crear la maquina
    instrucciones = models.TextField(max_length=255, blank=False, null=False, default="") # Instrucciones para crear la maquina
    # Creo una función para cuando se modifica el valor activa
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name_plural="Maquinas vulnerables"

#Las maquinas soportadas por el sistema serán: Maquinas Docker a partir de un Dockerfile, maquinas Docker generadas con un Docker Compose y Maquinas Virtuales
class MaquinaDocker(MaquinaVulnerable):
    archivo = models.FileField(upload_to='archivoZipDocker/', validators=[Validate_zip_file], blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk:
            # Si la máquina ya existe y se está modificando
            maquina = MaquinaDocker.objects.get(pk=self.pk)
            super().save(*args, **kwargs)
        # Si el nombre de la maquina ya existe
        elif MaquinaVulnerable.objects.filter(nombre=self.nombre).exists():
            raise ValidationError('El nombre de la máquina ya existe')
        else:
            try:
                with zipfile.ZipFile(self.archivo, 'r') as zip_ref:
                    temp_folder = 'maquinas_docker/'
                    zip_ref.extractall(temp_folder)
                    nombres_archivos = zip_ref.namelist()
                    nombre_carpeta = nombres_archivos[0]
                    os.rename(f"{temp_folder}{nombre_carpeta}", f"{temp_folder}{self.nombre}")
                    Validar_carpeta_docker_compose(self)

                    nombre_maquina = self.nombre.lower()
                    ruta_dockerfile = f'maquinas_docker/{self.nombre}/Dockerfile'
                    comando = f"docker build -t {nombre_maquina} maquinas_docker/{self.nombre}/."
                    subprocess.run(comando, shell=True, check=True)

                # Si todo es exitoso, confirmar la transacción
                with transaction.atomic():
                    super().save(*args, **kwargs)
            except subprocess.CalledProcessError as e:
                # Ocurrió un error, mostrar un mensaje de error si hay una solicitud disponible
                print(f"Error al crear la imagen: {e}, se elimina la máquina de la base de datos")
                raise ValidationError('Formato introducido incorrecto')

    def levantar_maquina_docker(self, relacion):
        print("Levantando la máquina")
        ruta_dockerfile = f'maquinas_docker/{self.nombre}/Dockerfile'
        comando = f"docker run --name {relacion.jugador.usuario.username} -d --rm {self.nombre.lower()}"
        try:
            subprocess.run(comando, shell=True, check=True)
            # Introduzco un archivo flag.txt en el contenedor recien levantado
            with open('flag.txt', 'w') as archivo:
                archivo.write(relacion.maquina_vulnerable.bandera_usuario_inicial)
            with open('flag2.txt', 'w') as archivo:
                archivo.write(relacion.maquina_vulnerable.bandera_usuario_root)
            comando = f"docker cp flag.txt {relacion.jugador.usuario.username}:/var/www/html/flag.txt"
            subprocess.run(comando, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error al levantar la máquina: {e}")
            return False
        try:
            comando = f"docker cp flag2.txt {relacion.jugador.usuario.username}:/etc/flag2.txt"
            subprocess.run(comando, shell=True, check=True)
            # Elimino el archivo flag.txt
            os.remove('flag.txt')
            os.remove('flag2.txt')
        except subprocess.CalledProcessError as e:
            print(f"Error al copiar el archivo: {e}")
            return False
        try:
            # Obtengo la ip
            comando = f"docker inspect -f '{{{{range .NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' {relacion.jugador.usuario.username}"
            direccion = subprocess.run(comando, shell=True, check=True, capture_output=True)
            coincidencia = re.search(r'(\d+\.\d+\.\d+\.\d+)', direccion.stdout.decode('utf-8'))
            direccion_ip = coincidencia.group(1)
            relacion.ip_address = direccion_ip
            comando=f"sudo ./iptables.sh add {relacion.jugador.usuario.username} {direccion_ip}"
            subprocess.run(comando, shell=True, check=True)
            print(f"La dirección IP de la máquina es: {direccion_ip}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error al obtener la dirección IP: {e}")
            self.detener_maquina_docker(relacion)
            return False

    def detener_maquina_docker(self, relacion):
        comando=f"docker rm -f {relacion.jugador.usuario.username}"
        try:
            subprocess.run(comando, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            exit_code = e.returncode
            return False
        if relacion.ip_address:
            comando=f"sudo ./iptables.sh del {relacion.ip_address}"
            subprocess.run(comando, shell=True, check=True)
        return True
    class Meta:
        verbose_name_plural = "Máquinas Docker"

class MaquinaDockerCompose(MaquinaVulnerable):
    #Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina Docker con un Docker Compose
    archivo = models.FileField(upload_to='archivoZipDockerCompose/', validators=[Validate_zip_file], blank=True)

    def save(self, *args, **kwargs):
        # Eliminar el archivo original
        if self.pk:
            # Si la máquina ya existe y se está modificando
            # - Obtengo la ruta del archivo anterior y la ruta de la nueva
            if self.archivo != MaquinaDockerCompose.objects.get(pk=self.pk).archivo:
                # Eliminaré la ruta del archivo anterior y la carpeta de la maquina, y ya luego guardaré el nuevo archivo
                pass
            else:
                maquina = MaquinaDockerCompose.objects.get(pk=self.pk)
                super().save(*args, **kwargs)
        else:
            # Después de validar que es un archivo zip
            with zipfile.ZipFile(self.archivo, 'r') as zip_ref:
                # Extract the contents of the zip file to a temporary folder
                temp_folder = 'maquinas_docker_compose/'
                zip_ref.extractall(temp_folder)
                Validar_carpeta_docker_compose(self)
            super().save(*args, **kwargs) # A parte de guardar el archivo, se extraerá el contenido del zip y se validará la estructura de la carpeta
    class Meta:
        verbose_name_plural = "Maquinas Docker Compose"
        
    def levantar_maquina_docker_compose(self, relacion):
        ruta_docker_compose = f'maquinas_docker_compose/{self.nombre}/docker-compose.yml'
        levantar_contenedor = f"PLAYER={relacion.jugador.usuario.username.lower()} docker-compose -f {ruta_docker_compose} -p 'proyecto_{relacion.jugador.usuario.username}' up -d"
        obtener_ip=f"docker exec proyecto_{relacion.jugador.usuario.username}_nginx_1 ifconfig eth0 | awk '/inet /" +  "{print $2}'" #Cambiar para casos generales
        try:
            # Obtengo la dirección IP de la maquina y el codigo de estado del comando
            subprocess.run(levantar_contenedor, shell=True, check=True) # Levantar el contenedor
            direccion = subprocess.run(obtener_ip, shell=True, check=True, capture_output=True) # Obtener la dirección IP
            coincidencia = re.search(r'(\d+\.\d+\.\d+\.\d+)', direccion.stdout.decode('utf-8'))
            if coincidencia:
                direccion_ip = coincidencia.group(1)
                relacion.ip_address = direccion_ip
                segmentar_red=f"sudo ./iptables.sh add {relacion.jugador.usuario.username.lower()} {direccion_ip}" # Ejecuto este script y si el codigo de estado es distinto de 0 entonces no se ha podido añadir la regla
                try:
                    salida = subprocess.run(segmentar_red, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    # Creo un hilo para detener la maquina
                    mi_hilo = threading.Thread(target=self.detener_maquina_docker_compose, args=(relacion,))
                    mi_hilo.start()
                    print(f"Error al segmentar la red: {e}")
                    return False
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error al levantar la máquina: {e}")
            return False
    def detener_maquina_docker_compose(self, relacion):
        ruta_docker_compose = f'maquinas_docker_compose/{self.nombre}/docker-compose.yml'
        comando=f"PLAYER={relacion.jugador.usuario.username} docker-compose -f {ruta_docker_compose} -p 'proyecto_{relacion.jugador.usuario.username}' down"
        try:
            subprocess.run(comando, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            exit_code = e.returncode
            return False
        if relacion.ip_address:
            comando=f"sudo ./iptables.sh del {relacion.ip_address}"
            subprocess.run(comando, shell=True, check=True)
        return True

class MaquinaVirtual(MaquinaVulnerable):
    #Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina virtual
    # Otros atributos...
    ip_maquina_virtual = models.CharField(max_length=25)
    class Meta:
        verbose_name_plural = "Maquinas Virtuales"

# Relacionar máquinas con el jugador
class MaquinaJugador(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    maquina_vulnerable = models.ForeignKey('MaquinaVulnerable', on_delete=models.CASCADE)
    activa = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=15, blank=True, null=True) #Dirección IP de la maquina vulnerable
    def __str__(self):
        estado = "activa" if self.activa else "inactiva"
        return f"{self.jugador.usuario.username} tiene la maquina {self.maquina_vulnerable.nombre}  {estado}"
    
    def save(self, *args, **kwargs):
        # Verifica si el nombre ha cambiado
        if self.pk is not None:
            original = MaquinaJugador.objects.get(pk=self.pk)
            if original.activa != self.activa:
                # Si se DESACTIVA la maquina
                if not self.activa:
                    if hasattr(self.maquina_vulnerable, 'maquinadocker'):
                        docker_instance = getattr(self.maquina_vulnerable, 'maquinadocker')
                        control = docker_instance.detener_maquina_docker(self)
                        if control:
                            self.ip_address = None
                            self.activa = False
                    elif hasattr(self.maquina_vulnerable, 'maquinadockercompose'):
                        compose_instance = getattr(self.maquina_vulnerable, 'maquinadockercompose')
                        control = compose_instance.detener_maquina_docker_compose(self)
                        if control:
                            self.ip_address = None
                            self.activa = False
                else:
                    #Si se ACTIVA la maquina
                    if hasattr(self.maquina_vulnerable, 'maquinadocker'):
                        # Levantar la maquina Docker
                        docker_instance = getattr(self.maquina_vulnerable, 'maquinadocker')
                        self.activa = docker_instance.levantar_maquina_docker(self)
                    elif hasattr(self.maquina_vulnerable, 'maquinadockercompose'):
                        compose_instance = getattr(self.maquina_vulnerable, 'maquinadockercompose')
                        self.activa = compose_instance.levantar_maquina_docker_compose(self)
                    elif hasattr(self.maquina_vulnerable, 'maquinavirtual'):
                        # Levantar la maquina Virtual
                        pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Relaciones jugadores con maquinas"

# Tabla para guardar las banderas que ha obtenido cada jugador
class PuntuacionJugador(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    maquina_vulnerable = models.ForeignKey(MaquinaVulnerable, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(default=0)
    fecha_obtencion = models.DateTimeField(auto_now_add=True)
    bandera = models.IntegerField(default=0) # 0: Bandera del usuario, 1: Bandera del root
    def __str__(self):
        estado = "del root" if self.bandera else "del usuario"
        return f"{self.jugador.usuario.username} ha obtenido la bandera {estado} de la maquina {self.maquina_vulnerable.nombre}"
    class Meta:
        verbose_name_plural = "Banderas de los jugadores"

# Funciones de disparadores
def crear_jugador_al_crear_usuario(sender, instance, created, **kwargs):
    if created:
        jugador = Jugador.objects.create(usuario=instance) #Crea el jugador
        maquinas_disponibles = MaquinaVulnerable.objects.all()
        for maquina in maquinas_disponibles:
            if jugador.puntuacion >= maquina.puntuacion_minima_activacion:
                MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=maquina)

#Crear relaciones con los jugadores cuando se crea una maquina Docker Compose
def crear_relacion_al_crear_maquina_docker_compose(sender, instance, created, **kwargs):
    if created:
        jugadores = Jugador.objects.all()
        for jugador in jugadores:
            if jugador.puntuacion >= instance.puntuacion_minima_activacion:
                MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=instance)

# Función para crear la realción maquina-jugador cuando se actualiza la puntuación de un jugador
def crear_relacion_al_actualizar_puntuacion(sender, instance, **kwargs):
    maquinas_disponibles = MaquinaVulnerable.objects.all()
    jugador = Jugador.objects.get(usuario=instance.usuario)
    for maquina in maquinas_disponibles:
        # Obtener el jugador
        if jugador.puntuacion >= maquina.puntuacion_minima_activacion:
            MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=maquina)





# Disparadores
post_save.connect(crear_relacion_al_actualizar_puntuacion, sender=Jugador) # Crear relaciones con los jugadores cuando se actualiza la puntuación
post_save.connect(crear_jugador_al_crear_usuario, sender=User) # Crear jugador y relaciones correspondientes con las maquinas
#post_save.connect(crear_relacion_al_crear_maquina, sender=MaquinaVulnerable) # Crear relaciones con los jugadores cuando se crea una maquina
post_save.connect(crear_relacion_al_crear_maquina_docker_compose, sender=MaquinaDockerCompose) # Crear relaciones con los jugadores cuando se crea una maquina Docker Compose
post_save.connect(crear_relacion_al_crear_maquina_docker_compose, sender=MaquinaDocker) # Crear relaciones con los jugadores cuando se crea una maquina Docker
post_save.connect(crear_relacion_al_crear_maquina_docker_compose, sender=MaquinaVulnerable) # Crear relaciones con los jugadores cuando se crea una maquina Docker
# ##################################################################
# Cuando se elimine una maquina se elimina su archivo y su carpeta
def delete_file_and_folder(sender, instance, **kwargs):
    if isinstance(instance, MaquinaDocker):
        try:
            os.remove(instance.archivo.path)
        except:
            pass
        try:
            directory_path = f'maquinas_docker/{instance.nombre}'
            shutil.rmtree(directory_path)
            print(f"Directorio '{directory_path}' eliminado con éxito")
        except OSError as e:
            print(f"Error al eliminar directorio: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
        try:
            comando = f"docker rmi {instance.nombre}"
            subprocess.run(comando, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error al eliminar la imagen: {e}")

# # Disparadores para eliminar los archivos y carpetas de las maquinas
post_delete.connect(delete_file_and_folder, sender=MaquinaDocker)

@receiver(pre_delete, sender=Jugador)
def delete_user(sender, instance, **kwargs):
    # Ejecutar el script para eliminar el usuario VPN
    comando = f"sudo ./createUserVPN.sh del {instance.usuario.username}"
    subprocess.run(comando, shell=True, check=True)

def obtener_tipo_maquina(maquina):
    print(maquina)
    if hasattr(maquina, 'maquinadocker'):
        return getattr(maquina, 'maquinadocker')
    elif hasattr(maquina, 'maquinadockercompose'):
        return getattr(maquina, 'maquinadockercompose')
    elif hasattr(maquina, 'maquinavirtual'):
        return getattr(maquina, 'maquinavirtual')
    else:
        return None
def jugador_conectado_vpn(usuario):
    return True # Suponemos que el usuario esta siempre conectado
    #comando = f"sudo ./createUserVPN.sh check {usuario}"
    try:
        #Obtengo el output del comando
        salida = subprocess.run(comando, shell=True, check=True, capture_output=True)
        #Si el output es 0 entonces el usuario está conectado
        if salida.returncode == 0:
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error al comprobar si el usuario está conectado: {e}")
        return False