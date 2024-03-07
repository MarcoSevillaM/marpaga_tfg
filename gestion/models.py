import zipfile
import os
import secrets
import subprocess
import re
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .functions import OverwriteStorage, Validate_zip_file, Validar_carpeta_docker_compose
from .functions import Up_docker_machine
from django.db.models.signals import pre_delete
from django.contrib import messages
import shutil
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

@receiver(pre_delete, sender=Jugador)
def delete_user(sender, instance, **kwargs):
    # Ejecutar el script para eliminar el usuario VPN
    comando = f"sudo ./createUserVPN.sh del {instance.usuario.username}"
    subprocess.run(comando, shell=True, check=True)

class MaquinaVulnerable(models.Model):
    DIFFICULT_CHOICES = (
        ('Facil', 'Facil'),
        ('Medio', 'Medio'),
        ('Dificl', 'Dificil'),
        ('Bestia', 'Bestia'),
    )
    nombre = models.CharField(max_length=255)
    nivel_dificultad = models.CharField(max_length=6, choices=DIFFICULT_CHOICES)
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
    #Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina Docker con una imagen correspondiente
    archivo = models.FileField(upload_to='archivoZipDocker/', validators=[Validate_zip_file], blank=True, null=True)

    def save(self, *args, **kwargs):
        # Eliminar el archivo original
        if self.pk:
            maquina = MaquinaDockerobjects.get(pk=self.pk)
            try:
                os.remove(maquina.archivo.path)
            except:
                pass
        super().save(*args, **kwargs) # A parte de guardar el archivo, se extraerá el contenido del zip y se validará la estructura de la carpeta
        # Después de validar que es un archivo zip
        with zipfile.ZipFile(self.archivo, 'r') as zip_ref:
            # Extract the contents of the zip file to a temporary folder
            temp_folder = 'maquinas_docker/'
            zip_ref.extractall(temp_folder)
            # Obtengo el nombre del archivo extraido
            nombre_carpeta = os.listdir(temp_folder)[0] # Obtengo el nombre de la carpeta
            # Cambio el nombre de la carpte al nombre de la maquina
            os.rename(f"{temp_folder}{nombre_carpeta}", f"{temp_folder}{self.nombre}")
            Validar_carpeta_docker_compose(self)

            # Obtengo el nombre de la maquina
            nombre_maquina = self.nombre
            # Obtengo la ruta donde esta el Dockerfile
            ruta_dockerfile = f'maquinas_docker/{nombre_maquina}/Dockerfile'
            # Levantar la maquina Docker
            comando = f"docker build -t {nombre_maquina} maquinas_docker/{nombre_maquina}/."
            try:
                subprocess.run(comando, shell=True, check=True) 
            except subprocess.CalledProcessError as e:
                # No se puede crear la imagen por lo tanto se elimina la maquina de la base de datos
                print(f"Error al crear la imagen: {e}, se elimina la maquina de la base de datos")
                self.delete()
    class Meta:
        verbose_name_plural = "Maquinas Docker"

class MaquinaDockerCompose(MaquinaVulnerable):
    #Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina Docker con un Docker Compose
    archivo = models.FileField(upload_to='archivoZipDockerCompose/', validators=[Validate_zip_file])

    def save(self, *args, **kwargs):
        # Eliminar el archivo original
        if self.pk:
            maquina = MaquinaDockerCompose.objects.get(pk=self.pk)
            try:
                os.remove(maquina.archivo.path)
            except:
                pass
        super().save(*args, **kwargs) # A parte de guardar el archivo, se extraerá el contenido del zip y se validará la estructura de la carpeta
        # Después de validar que es un archivo zip
        with zipfile.ZipFile(self.archivo, 'r') as zip_ref:
            # Extract the contents of the zip file to a temporary folder
            temp_folder = 'maquinas_docker_compose/'
            zip_ref.extractall(temp_folder)
            validar_carpeta_docker_compose(self)
    class Meta:
        verbose_name_plural = "Maquinas Docker Compose"

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
                        nombre_maquina = self.maquina_vulnerable.nombre
                        comando=f"docker rm -f {self.jugador.usuario.username}"
                        subprocess.run(comando, shell=True, check=True)
                        if self.ip_address:
                            comando=f"sudo ./iptables.sh del {self.ip_address}"
                            subprocess.run(comando, shell=True, check=True)
                        self.ip_address = None
                    elif hasattr(self.maquina_vulnerable, 'maquinadockercompose'):
                        ruta_docker_compose = f'maquinas_docker_compose/{self.maquina_vulnerable.nombre}/docker-compose.yml'
                        comando=f"PLAYER={self.jugador.usuario.username} docker-compose -f {ruta_docker_compose} -p 'proyecto_{self.jugador.usuario.username}' down"
                        try:
                            subprocess.run(comando, shell=True, check=True)
                        except subprocess.CalledProcessError as e:
                            exit_code = e.returncode
                            # Do something with the exit code
                            #messages.error(f"Command exited with code: {exit_code}")
                            self.activa = True
                        if self.ip_address:
                            comando=f"sudo ./iptables.sh del {self.ip_address}"
                            subprocess.run(comando, shell=True, check=True)
                        self.ip_address = None
                else:
                    #Si se ACTIVA la maquina
                    if hasattr(self.maquina_vulnerable, 'maquinadocker'):
                        # Levantar la maquina Docker
                        control = Up_docker_machine(self.maquina_vulnerable, self.jugador)
                        if control:
                            # Obtengo la ip
                            comando = f"docker inspect -f '{{{{range .NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' {self.jugador.usuario.username}"
                            direccion = subprocess.run(comando, shell=True, check=True, capture_output=True)
                            coincidencia = re.search(r'(\d+\.\d+\.\d+\.\d+)', direccion.stdout.decode('utf-8'))
                            if coincidencia:
                                direccion_ip = coincidencia.group(1)
                                self.ip_address = direccion_ip
                                comando=f"sudo ./iptables.sh add {self.jugador.usuario.username} {direccion_ip}"
                                subprocess.run(comando, shell=True, check=True)
                        else:
                            self.activa = False
                    elif hasattr(self.maquina_vulnerable, 'maquinadockercompose'):
                        # Levantar la maquina Docker Compose
                        ruta_docker_compose = f'maquinas_docker_compose/{self.maquina_vulnerable.nombre}/docker-compose.yml'
                        comando = f"PLAYER={self.jugador.usuario.username.lower()} docker-compose -f {ruta_docker_compose} -p 'proyecto_{self.jugador.usuario.username}' up -d"
                        # Obtengo la dirección IP de la maquina y el codigo de estado del comando
                        try:
                            subprocess.run(comando, shell=True, check=True)
                            comando=f"docker exec proyecto_{self.jugador.usuario.username}_nginx_1 ifconfig eth0 | awk '/inet /" +  "{print $2}'" #Cambiar para casos generales
                            direccion = subprocess.run(comando, shell=True, check=True, capture_output=True)
                            coincidencia = re.search(r'(\d+\.\d+\.\d+\.\d+)', direccion.stdout.decode('utf-8'))
                            if coincidencia:
                                direccion_ip = coincidencia.group(1)
                                self.ip_address = direccion_ip
                                print(direccion_ip)
                                comando=f"sudo ./iptables.sh add {self.jugador.usuario.username.lower()} {direccion_ip}"
                                subprocess.run(comando, shell=True, check=True)
                        except subprocess.CalledProcessError as e:
                            #exit_code = e.returncode
                            # Do something with the exit code
                            #messages.error(f"Command exited with code: {exit_code}")
                            #messages.error(request, f"Error al levantar la maquina")
                            self.activa = False
                    elif hasattr(self.maquina_vulnerable, 'maquinavirtual'):
                        # Levantar la maquina Virtual
                        pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Relaciones jugadores con maquinas"


# Funciones de disparadores
#@receiver(post_save, sender=User)
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
 

# Disparadores
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
