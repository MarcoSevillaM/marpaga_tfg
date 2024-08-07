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
import datetime

# # La base de datos contendrá unos usuarios denominados "jugadores" con su perfil propio
class Jugador(models.Model):
    """

    Clase que representa a un jugador del juego

    Attributes:
        usuario (User): El usuario que representa al jugador
        puntuacion (int): La puntuación del jugador
        foto_perfil (ImageField): La foto de perfil del jugador
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='photoPersonal/', blank=True, null=True, storage=OverwriteStorage(), default='photoPersonal/default.jpg')
    
    # Cuando se crea un jugador se le crea un cliente vpn por lo que se ejecuta el script createUserVPN.sh
    def save(self, *args, **kwargs):
        """
        Función que guarda el objeto en la base de datos

        Args:
            self (Jugador): El objeto de la clase Jugador
            *args: Argumentos adicionales
            **kwargs: Argumentos adicionales
        """
        if self.pk is None: # Si es un nuevo usuario
            super().save(*args, **kwargs)
            # Ejecutar el script para crear el usuario VPN
            comando = f"sudo ./createUserVPN.sh add {self.usuario.username}"
            subprocess.run(comando, shell=True, check=True)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        """
        Retorna el nombre del usuario

        Returns:
            str: El nombre del usuario
        """
        return self.usuario.username
    class Meta: 
        verbose_name_plural="Jugadores"
    @property
    def puntuacion(self):
        return self.obtener_puntuacion()
    def obtener_puntuacion(self):
        return PuntuacionJugador.objects.filter(jugador=self).aggregate(Sum('puntuacion'))['puntuacion__sum'] or 0

class MaquinaVulnerable(models.Model):  
    """
    Clase que representa una máquina vulnerable

    Attributes:
        nombre (str): El nombre de la máquina
        nivel_dificultad (str): El nivel de dificultad de la máquina
        puntuacion_minima_activacion (int): La puntuación mínima para activar la máquina
        descripcion (str): La descripción de la máquina
        bandera_usuario_inicial (str): La bandera del usuario inicial
        bandera_usuario_root (str): La bandera del usuario root
        instrucciones (str): Las instrucciones para crear la máquina
    """
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
        """
        Retorna el nombre de la máquina

        Returns:
            str: El nombre de la máquina
        """
        return self.nombre
    class Meta:
        verbose_name_plural="Maquinas vulnerables"

#Las maquinas soportadas por el sistema serán: Maquinas Docker a partir de un Dockerfile, maquinas Docker generadas con un Docker Compose y Maquinas Virtuales
class MaquinaDocker(MaquinaVulnerable):
    """
    Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina Docker

    Attributes:
        archivo (FileField): El archivo que contiene la configuración de la máquina
    """
    archivo = models.FileField(upload_to='archivoZipDocker/', validators=[Validate_zip_file], blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Función que guarda el objeto en la base de datos así como gestiona la creación de la máquina dentor de Docker y guardar en el directorio correspondiente los ficheros

        Args:
            self (MaquinaDocker): El objeto de la clase MaquinaDocker
            *args: Argumentos adicionales
            **kwargs: Argumentos adicionales
        """
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
                    # Cambio el nombre de la carpeta y quito los respacios por '_'
                    nombre_carpeta_new = nombre_carpeta.replace(' ', '_')
                    self.nombre=self.nombre.replace(' ', '_')
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
                raise ValidationError(f'Error al importar la imagen {e}')

    def levantar_maquina_docker(self, relacion):
        """
        Función que levanta una instancia de la máquina en Docker

        Args:
            self (MaquinaDocker): El objeto de la clase MaquinaDocker
            relacion (MaquinaJugador): La relación entre la máquina y el jugador

        Returns:
            bool: True si la máquina se ha levantado correctamente, False en caso contrario
        """
        comando = f"docker run --name {relacion.jugador.usuario.username} -d --rm {self.nombre.lower()}"
        try:
            subprocess.run(comando, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error al levantar la máquina: {e}")
            self.detener_maquina_docker(relacion)
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
        """
        Función que detiene una instancia de la máquina en Docker

        Args:
            self (MaquinaDocker): El objeto de la clase MaquinaDocker
            relacion (MaquinaJugador): La relación entre la máquina y el jugador

        Returns:
            bool: True si la máquina se ha detenido correctamente, False en caso contrario
        """
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
    """
    Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina Docker con un Docker Compose

    Attributes:
        archivo (FileField): El archivo que contiene la configuración para levantar el docker-compose

    """
    #Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina Docker con un Docker Compose
    archivo = models.FileField(upload_to='archivoZipDockerCompose/', validators=[Validate_zip_file], blank=True)

    def save(self, *args, **kwargs):
        """
        Función que guarda el objeto en la base de datos así como gestiona la creación de la máquina dentor de Docker y guardar en el directorio correspondiente los ficheros

        Args:
            self (MaquinaDockerCompose): El objeto de la clase MaquinaDockerCompose
            *args: Argumentos adicionales
            **kwargs: Argumentos adicionales
        """
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
        """
        Función que levanta una instancia de la máquina en Docker Compose

        Args:
            self (MaquinaDockerCompose): El objeto de la clase MaquinaDockerCompose
            relacion (MaquinaJugador): La relación entre la máquina y el jugador

        Returns:
            bool: True si la máquina se ha levantado correctamente, False en caso contrario
        """
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
                    print(f"Maquina limitada al usuario {relacion.jugador.usuario.username} con la dirección IP {direccion_ip}")
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
        """
        Función que detiene una instancia de la máquina en Docker Compose

        Args:
            self (MaquinaDockerCompose): El objeto de la clase MaquinaDockerCompose
            relacion (MaquinaJugador): La relación entre la máquina y el jugador
        
        Returns:
            bool: True si la máquina se ha detenido correctamente, False en caso contrario
        """
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
    """
    Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina virtual

    Attributes:
        ip_maquina_virtual (str): La dirección IP de la máquina virtual
        otros_atributos (str): Otros atributos pendientes de implementar
    """
    #Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina virtual
    # Otros atributos...
    ip_maquina_virtual = models.CharField(max_length=25)
    class Meta:
        verbose_name_plural = "Maquinas Virtuales"

# Relacionar máquinas con el jugador
class MaquinaJugador(models.Model):
    """
    Clase que relaciona a un jugador con una máquina

    Attributes:
        jugador (Jugador): El jugador relacionado
        maquina_vulnerable (MaquinaVulnerable): La máquina relacionada
        activa (bool): True si la máquina está activa, False en caso contrario
        ip_address (str): La dirección IP de la máquina
        tiempo_activa (int): El tiempo que ha estado activa la máquina
        momento_activacion (DateTimeField): El momento en el que se activa la máquina
    """
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    maquina_vulnerable = models.ForeignKey('MaquinaVulnerable', on_delete=models.CASCADE)
    activa = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=15, blank=True, null=True) #Dirección IP de la maquina vulnerable
    tiempo_activa = models.BigIntegerField(null=True, blank=True) # Tiempo que ha estado activa la maquina
    momento_activacion = models.DateTimeField(auto_now_add=True, null=True, blank=True) # Momento en el que se activa la maquina
    def __str__(self):
        """
        Retorna el nombre del jugador y la máquina

        Returns:
            str: El nombre del jugador y la máquina
        """
        estado = "activa" if self.activa else "inactiva"
        return f"{self.jugador.usuario.username} tiene la maquina {self.maquina_vulnerable.nombre}  {estado}"
    
    # Paso un parámetro que es el tiempo que ha estado activa la máquina
    def actualizar_tiempo_activa(self, tiempo):
        """
        Función que actualiza el tiempo que ha estado activa la máquina
        
        Args:
            self (MaquinaJugador): El objeto de la clase MaquinaJugador
            tiempo (int): El tiempo que ha estado activa la máquina
        """
        if self.tiempo_activa is None:
            self.tiempo_activa = tiempo
        else:
            self.tiempo_activa = tiempo + self.tiempo_activa
        self.save()

    def obtener_tiempo_total_activa(self):
        """
        Función que obtiene el tiempo total que ha estado activa la máquina

        Returns:
            int: Tiempo total que ha estado activa la máquina
        """
        if self.tiempo_activa is None or self.tiempo_activa == 0:
            return 0

        seconds = self.tiempo_activa
        # Convertimos los segundos en horas, minutos y segundos
        td = datetime.timedelta(seconds=seconds)
        total_seconds = td.total_seconds()
        hours = total_seconds // 3600
        remainder = total_seconds % 3600
        minutes = remainder // 60
        seconds = remainder % 60

        # Construimos la cadena de tiempo legible
        result = []
        if hours > 0:
            result.append(f"{int(hours)} {'hora' if hours == 1 else 'horas'}")
        if minutes > 0:
            result.append(f"{int(minutes)} {'minuto' if minutes == 1 else 'minutos'}")
        if seconds > 0:
            result.append(f"{int(seconds)} {'segundo' if seconds == 1 else 'segundos'}")

        return ", ".join(result)

    # Método para convertir el tiempo en un formato legible de horas, minutos y segundos
    @property
    def obtener_tiempo(self):
        """
        Función que obtiene el tiempo en un formato legible de horas, minutos y segundos

        Returns:
            str: El tiempo en un formato legible de horas, minutos y segundos
        
        """
        tiempo = self.tiempo_activa
        horas = tiempo // 3600
        minutos = (tiempo % 3600) // 60
        segundos = tiempo % 60
        return "{:05}h:{:02}min:{:02}sec".format(int(horas), int(minutos), int(segundos))
        #return horas, minutos, segundos

    def save(self, *args, **kwargs):
        """
        Función que guarda el objeto en la base de datos y gestiona la activación y desactivación de la máquina,
        adicionalmente establece la variable activa en función de lo que ocurra.

        Args:
            self (MaquinaJugador): El objeto de la clase MaquinaJugador
            *args: Argumentos adicionales
            **kwargs: Argumentos adicionales
        """
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
                    elif hasattr(self.maquina_vulnerable, 'maquinavirtual'):
                        pass
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
    """
    Clase que guarda las banderas que ha obtenido cada jugador

    Attributes:
        jugador (Jugador): El jugador que ha obtenido la bandera
        maquina_vulnerable (MaquinaVulnerable): La máquina de la que ha obtenido la bandera
        puntuacion (int): La puntuación obtenida
        fecha_obtencion (DateTimeField): La fecha en la que se ha obtenido la bandera
        bandera (int): 0 si es la bandera del usuario, 1 si es la bandera del root
    """
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    maquina_vulnerable = models.ForeignKey(MaquinaVulnerable, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(default=0)
    fecha_obtencion = models.DateTimeField(auto_now_add=True)
    bandera = models.IntegerField(default=0) # 0: Bandera del usuario, 1: Bandera del root
    def __str__(self):
        """
        Retorna una cadena en formato legible de la relacion puntuacion jugador

        Returns:
            str: La relación establecida entre el jugador y la máquina, así como si esta activa o no
        """
        estado = "flag 2" if self.bandera else "flag 1"
        return f"{self.jugador.usuario.username} ha obtenido la {estado} de la maquina {self.maquina_vulnerable.nombre}"
    class Meta:
        verbose_name_plural = "Banderas de los jugadores (puntuaciones)"

# Tabla para guardar las valoraciones de las banderas de las maquinas
class ValoracionJugador(models.Model):
    """
    Clase que guarda las valoraciones de las banderas de las máquinas

    Attributes:
        puntuacion_jugador (PuntuacionJugador): La puntuación del jugador
        valoracion (int): La valoración de la bandera
        fecha_valoracion (DateTimeField): La fecha en la que se ha valorado la bandera
    """
    puntuacion_jugador = models.ForeignKey(PuntuacionJugador, on_delete=models.CASCADE) # El jugador solo puede valorar las banderas que ha obtenido
    valoracion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    fecha_valoracion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        """
        Retorna una cadena en formato legible de la relacion valoracion jugador

        Returns:
            str: La relación establecida entre el jugador y la máquina, así como si esta activa o no
        """
        return f"{self.puntuacion_jugador.jugador.usuario.username} ha valorado la flag {self.puntuacion_jugador.bandera} de la maquina {self.puntuacion_jugador.maquina_vulnerable.nombre} con un {self.valoracion}"
    class Meta:
        verbose_name_plural = "Valoraciones de los jugadores"
# Funciones de disparadores
def crear_jugador_al_crear_usuario(sender, instance, created, **kwargs):
    """
    Función que funciona como disparador y que crea un jugador cuando se crea un usuario

    Args:
        sender: El objeto que envía la señal
        instance: La instancia del objeto que envía la señal
        created: True si se ha creado el objeto, False en caso contrario
        **kwargs: Argumentos adicionales
    """
    if created:
        jugador = Jugador.objects.create(usuario=instance) #Crea el jugador
        maquinas_disponibles = MaquinaVulnerable.objects.all()
        for maquina in maquinas_disponibles:
            if jugador.obtener_puntuacion() >= maquina.puntuacion_minima_activacion:
                MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=maquina)

#Crear relaciones con los jugadores cuando se crea una maquina Docker Compose
def crear_relacion_al_crear_maquina_docker_compose(sender, instance, created, **kwargs):
    """
    Función que funciona como disparador y que crea una relación entre la máquina y el jugador cuando se crea una máquina Docker Compose
    
    Args:
        sender: El objeto que envía la señal
        instance: La instancia del objeto que envía la señal
        created: True si se ha creado el objeto, False en caso contrario
        **kwargs: Argumentos adicionales
    """
    if created:
        jugadores = Jugador.objects.all()
        for jugador in jugadores:
            if jugador.obtener_puntuacion() >= instance.puntuacion_minima_activacion:
                MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=instance)

# Función para crear la realción maquina-jugador cuando se actualiza la puntuación de un jugador
def crear_relacion_al_actualizar_puntuacion(sender, instance, **kwargs):
    """
    Función que funciona como disparador y que crea una relación entre la máquina y el jugador cuando se actualiza la puntuación de un jugador

    Args:
        sender: El objeto que envía la señal
        instance: La instancia del objeto que envía la señal
        **kwargs: Argumentos adicionales
    """
    maquinas_disponibles = MaquinaVulnerable.objects.all()
    jugador = Jugador.objects.get(usuario=instance.usuario)
    for maquina in maquinas_disponibles:
        # Obtener el jugador
        if jugador.obtener_puntuacion() >= maquina.puntuacion_minima_activacion:
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
    """
    Función que elimina el archivo y la carpeta de una máquina cuando se elimina la máquina

    Args:
        sender: El objeto que envía la señal
        instance: La instancia del objeto que envía la señal
        **kwargs: Argumentos adicionales
    """
    
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
    """
    Función que elimina el archivo de configuración VPN y el usuario VPN

    Args:
        sender: El objeto que envía la señal
        instance: La instancia del objeto que envía la señal
        **kwargs: Argumentos adicionales
    """
    # Ejecutar el script para eliminar el usuario VPN
    comando = f"sudo ./createUserVPN.sh del {instance.usuario.username}"
    subprocess.run(comando, shell=True, check=True)

def obtener_tipo_maquina(maquina):
    """
    Función que obtiene el tipo de máquina

    Args:
        maquina (MaquinaVulnerable): La máquina de la que se obtendrá el tipo

    Returns:
        str: El tipo de máquina, si es Docker, Docker Compose o Virtual
    """
    if hasattr(maquina, 'maquinadocker'):
        return getattr(maquina, 'maquinadocker')
    elif hasattr(maquina, 'maquinadockercompose'):
        return getattr(maquina, 'maquinadockercompose')
    elif hasattr(maquina, 'maquinavirtual'):
        return getattr(maquina, 'maquinavirtual')
    else:
        return None

def jugador_conectado_vpn(usuario):
    """
    Función que comprueba si un usuario está conectado a la VPN

    Args:
        usuario (str): El nombre del usuario

    Returns:
        bool: True si el usuario está conectado, False en caso contrario
    """
    #return True # Suponemos que el usuario esta siempre conectado
    comando = f"sudo ./createUserVPN.sh check {usuario}"
    try:
        #Compruebo si el usuario esta conectado o por lo menos ha estado conectado en algún momento
        print("Llega aqui con el usuario: ", usuario)
        salida = subprocess.run(comando, shell=True, check=True, capture_output=True)
        #print(f"Output del comando: {salida}")
        #Si el output es 0 entonces el usuario está conectado
        if salida.returncode == 0:
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error al comprobar si el usuario está conectado: {e}")
        return False