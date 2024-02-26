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

def inicio(request):
    return render(request, 'gestion/index.html')

def registro(request):
    if request.method == 'POST':
        form = RegistrarJugador(request.POST)
        if form.is_valid():
            user = form.save()  # Guarda el usuario y obtén el objeto User
            user.is_active = False
            user.save()
            subject = 'Activa tu cuenta'
            message = render_to_string('gestion/account_activation_email.html', {
                'user': user,
                'domain': settings.EMAIL_NAME_HOST,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email_message = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [user.email])
            email_message.content_subtype = "html"
            #send_mail(subject, message, settings.EMAIL_HOST_USER, ['marcosevillam@gmail.com']) # Enviar el correo
            email_message.send()
            
            messages.success(request, 'Por favor, verifica tu correo electrónico para activar tu cuenta.')
            return redirect('registro')
    else:
            form = RegistrarJugador()
    context = {'form' : form}
    return render(request, 'gestion/registro.html', context)

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, '¡Tu cuenta ha sido activada!')
        return redirect('login')
    else:
        messages.error(request, 'El enlace de activación es inválido o ha expirado.')
        return redirect('login') 