from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from gestion.functions import validate_zip_file, validar_carpeta_docker_compose
import zipfile, os, secrets
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
from django.dispatch import receiver

# # La base de datos contendrá unos usuarios denominados "jugadores" con su perfil propio
class Jugador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nivel = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)]) # Para desbloquear diferentes maquinas
    puntuacion = models.IntegerField(default=0) #Se usará para el ranking y dependerá de las banderas obtenidas en cada maquina, su dificultad y tiempo en conseguirlo.
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    
    def __str__(self):
        return self.usuario.username
    class Meta: 
        verbose_name_plural="Jugadores"

class MaquinaVulnerable(models.Model):
    DIFFICULT_CHOICES = (
        ('Facil', 'Facil'),
        ('Medio', 'Medio'),
        ('Dificl', 'Dificil'),
        ('Insano', 'Insano'),
    )
    nombre = models.CharField(max_length=255)
    nivel_dificultad = models.CharField(max_length=6, choices=DIFFICULT_CHOICES)
    nivel_minimo_activacion = models.IntegerField(default=1)
    bandera_usuario_inicial = models.CharField(max_length=25, default=secrets.token_hex(12)) #Tendrá que coincidir con la bandera del usuario en la maquina
    bandera_usuario_root = models.CharField(max_length=25, default=secrets.token_hex(12)) #Tendrá que coincidicir con la bandera del root rn la maquina

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name_plural="Maquinas vulnerables"

#Las maquinas soportadas por el sistema serán: Maquinas Docker a partir de un Dockerfile, maquinas Docker generadas con un Docker Compose y Maquinas Virtuales
class MaquinaDocker(MaquinaVulnerable):
    #Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina Docker con una imagen correspondiente
    imagen_docker = models.CharField(max_length=255)
    puerto_exposicion = models.IntegerField()
    # Otros atributos...

    class Meta:
        verbose_name_plural = "Maquinas Docker"

class MaquinaDockerCompose(MaquinaVulnerable):
    #Clase que hereda de MaquinaVulnerable la cual contiene datos para iniciar una maquina Docker con un Docker Compose
    archivo = models.FileField(upload_to='archivoZipDockerCompose/', validators=[validate_zip_file])

    def save(self, *args, **kwargs):
        # Eliminar el archivo original
        if self.pk:
            maquina = MaquinaDockerCompose.objects.get(pk=self.pk)
            os.remove(maquina.archivo.path)
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
    def guardar_con_ip(self, ip_address):
        # Verificar si el modelo está activo antes de almacenar la dirección IP
        if self.activa:
            self.ip_address = ip_address
            self.save()
        else:
            self.ip_address = None
            self.save()
    class Meta:
        verbose_name_plural = "Relaciones jugadores con maquinas"


# Funciones de disparadores
@receiver(post_save, sender=User)
def crear_jugador_al_crear_usuario(sender, instance, created, **kwargs):
    if created:
        jugador = Jugador.objects.create(usuario=instance) #Crea el jugador
        maquinas_disponibles = MaquinaVulnerable.objects.all()
        for maquina in maquinas_disponibles:
            if jugador.nivel >= maquina.nivel_minimo_activacion:
                MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=maquina)

# def crear_relacion_al_crear_maquina(sender, instance, created, **kwargs):
#     if created:
#         maquinas_disponibles = MaquinaVulnerable.objects.all()
#         jugadores = Jugador.objects.all()
#         for maquina in maquinas_disponibles:
#             for jugador in jugadores:
#                 if jugador.nivel >= maquina.nivel_minimo_activacion:
#                     MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=maquina)
#Crear relaciones con los jugadores cuando se crea una maquina Docker Compose
def crear_relacion_al_crear_maquina_docker_compose(sender, instance, created, **kwargs):
    if created:
        print("Se intenta crear")
        jugadores = Jugador.objects.all()
        for jugador in jugadores:
            if jugador.nivel >= instance.nivel_minimo_activacion:
                MaquinaJugador.objects.get_or_create(jugador=jugador, maquina_vulnerable=instance)
        

# Disparadores
post_save.connect(crear_jugador_al_crear_usuario, sender=User) # Crear jugador y relaciones correspondientes con las maquinas
#post_save.connect(crear_relacion_al_crear_maquina, sender=MaquinaVulnerable) # Crear relaciones con los jugadores cuando se crea una maquina
post_save.connect(crear_relacion_al_crear_maquina_docker_compose, sender=MaquinaDockerCompose) # Crear relaciones con los jugadores cuando se crea una maquina Docker Compose
post_save.connect(crear_relacion_al_crear_maquina_docker_compose, sender=MaquinaDocker) # Crear relaciones con los jugadores cuando se crea una maquina Docker
post_save.connect(crear_relacion_al_crear_maquina_docker_compose, sender=MaquinaVulnerable) # Crear relaciones con los jugadores cuando se crea una maquina Docker
# ##################################################################