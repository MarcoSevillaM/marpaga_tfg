from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrarJugador(UserCreationForm):
    """
    Formulario para registrar un jugador

    Atributes:
        UserCreationForm (Form): Formulario de creación de usuario
    """
    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password1', 'password2']