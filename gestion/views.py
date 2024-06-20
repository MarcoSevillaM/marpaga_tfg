# Todo el codigo se escribe para generar un autodoc y sphinx
from django.http import HttpResponse
from django.shortcuts import render, redirect

#Se usa para la función registro la cual se encarga de arrastrar los valores del usuario User de Django
from .forms import RegistrarJugador

#Para la funcion de personal la cual se encarga de pasar los datos a la pagina personal del usuario
from .models import Jugador
from django.contrib.auth.models import User

#Para gestionar la sesion de la pagina personal, un decorador es algo que permite dar una funcionalidad extra 
from django.contrib.auth.decorators import login_required

#Gestionar subprocesos para Docker
import subprocess, threading
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm

#Para enviar correos y gestionar la activacion de la cuenta
from django.contrib.sites.shortcuts import get_current_site # Para obtener el dominio actual
from django.template.loader import render_to_string # Para renderizar el mensaje del correo
from .tokens import account_activation_token # Para generar el token de activación
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode # Para codificar y decodificar el token
from django.utils.encoding import force_bytes # Para convertir el token en bytes y texto
from django.utils.encoding import force_str # Para convertir el token en texto
from django.core.mail import EmailMessage
from django.conf import settings # Para obtener el dominio actual
from django.contrib import messages # Para la gestion de los mensajes
from django.contrib.auth import login # Para iniciar sesión
import time # Para el hilo que elimina los usuarios inactivos
# Cuando el usuario ha olvidado la constraseña
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

# Funcion del hilo para eliminar los usuarios inactivos
def remove_inactive_users(user):
    """
    Elimina los usuarios que no han activado su cuenta en el ultimo minuto

    Args:
        user (User): El usuario que se eliminará si no ha activado su cuenta

    Returns:
        None
    """
    time.sleep(60) # Espera 1 minuto
    user = User.objects.get(pk=user.pk)
    print(user.is_active)
    if user.is_active == False:
        user.delete()

def inicio(request):
    """
    Función que renderiza la página de inicio

    Args:
        request (HttpRequest): La petición HTTP

    Returns:
        HttpResponse: La respuesta HTTP
    """
    return render(request, 'gestion/index.html')

def registro(request):
    """
    Función que renderiza la página de registro, en caso de que se haya enviado el formulario, se encarga de crear el usuario y enviar el correo de activación

    Args:
        request (HttpRequest): La petición HTTP

    Returns:
        HttpResponse: La respuesta HTTP
    """
    if request.method == 'POST':
        form = RegistrarJugador(request.POST)
        if form.is_valid():
            user = form.save()  # Guarda el usuario y obtén el objeto User
            user.is_active = False
            user.save()
            # Creo un hilo que se ejecutará después de 1 minuto
            mi_hilo = threading.Thread(target=remove_inactive_users, args=(user,))
            mi_hilo.start()
            subject = 'Activa tu cuenta'
            message = render_to_string('gestion/account_activation_email.html', {
                'user': user,
                'domain': settings.EMAIL_NAME_HOST,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email_message = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email])
            email_message.content_subtype = "html"
            email_message.send()
            
            messages.success(request, 'Por favor, verifica tu correo electrónico para activar tu cuenta.')
            return redirect('registro')
    else:
            form = RegistrarJugador()
    context = {'form' : form}
    return render(request, 'gestion/registro.html', context)

def activate(request, uidb64, token):
    """
    Función que activa la cuenta del usuario

    Args:
        request (HttpRequest): La petición HTTP
        uidb64 (str): El ID del usuario codificado en base64
        token (str): El token de activación
    
    Returns:
        Redirect: Redirige a la página de inicio de sesión si la activación fue exitosa, de lo contrario, redirige a la página de inicio de sesión con un mensaje de error
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('login')
    else:
        messages.error(request, 'El enlace de activación es inválido o ha expirado.')
        return redirect('login') 

# Vistas para contraseña olvidada

class CustomPasswordResetView(PasswordResetView):
    """
    Clase que hereda de la página de restablecimiento de contraseña nativa de Django mostrando un formulario para restablecer la contraseña

    Atributes:
        template_name (str): La plantilla de la página
        user (User): El usuario que ha solicitado restablecer la contraseña
    """
    template_name = 'gestion/reset_passwd.html'
    user=None
    def form_valid(self, form):
        """
        Función que se ejecuta cuando el formulario es válido

        Args:
            form (Form): El formulario de restablecimiento de contraseña

        Returns:
            response: La respuesta HTTP con el formulario válido
        """
        response = super().form_valid(form)
        mensaje = f"Restablecimiento de contraseña enviado\n"
        messages.success(self.request, mensaje)
        mensaje = f"Le enviaremos intstruccciones por correo electrónico para configurar su contraseña, si existe una cuenta con el correo electrónico que ingresó. Debería recibirlas en breve.\n"
        messages.success(self.request, mensaje)
        mensaje = f"Si no recibe un correo electrónico, asegúrese de haber ingresado la dirección con la que se registró y verifique su carpeta de correo no deseado."
        messages.success(self.request, mensaje)
        mensaje = f"Volver a inicio\n"
        messages.info(self.request, mensaje)
        return response

class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Clase que hereda de la página de restablecimiento de contraseña nativa de Django cuando el correo de restablecimiento de contraseña ha sido enviado
    """
    template_name = 'gestion/reset_passwd.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Clase que hereda de la página de restablecimiento de contraseña nativa de Django mostrando un formulario para restablecer la contraseña

    Atributes:
        template_name (str): La plantilla de la página
    """
    template_name = 'gestion/reset_passwd_confirm.html'

    def form_valid(self, form):
        """
        Función que se ejecuta cuando el formulario es válido

        Args:
            form (Form): El formulario de restablecimiento de contraseña
        
        Returns:
            response: La respuesta HTTP con el formulario válido
        """
        response = super().form_valid(form)
        mensaje = f"Restablecimiento de contraseña completado\n"
        messages.success(self.request, mensaje)
        mensaje = f"Su contraseña ha sido restablecida. Ahora puede continuar e iniciar sesión.\n"
        messages.success(self.request, mensaje)
        mensaje = f"Iniciar sesión\n"
        messages.add_message(self.request, messages.INFO, mensaje)
        return response

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Clase que hereda de la página de restablecimiento de contraseña nativa de Django cuando el restablecimiento de contraseña ha sido completado
    """
    template_name = 'gestion/reset_passwd.html'