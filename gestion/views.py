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

def inicio(request):
    return render(request, 'gestion/index.html')

def registro(request):
    if request.method == 'POST':
        form = RegistrarJugador(request.POST)
        if form.is_valid():
            user = form.save()  # Guarda el usuario y obtén el objeto User
            return redirect('inicio')
    else:
            form = RegistrarJugador()
    context = {'form' : form}
    return render(request, 'gestion/registro.html', context)