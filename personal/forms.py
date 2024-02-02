from django import forms
from django.contrib.auth.forms import UserCreationForm

class GestionActivacionMaquinas(UserCreationForm):

    class Meta:
        fields = ['maquina_id', 'estado', 'ya_existe']