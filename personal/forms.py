from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from gestion.models import Jugador, MaquinaJugador, MaquinaVulnerable, MaquinaDocker, MaquinaDockerCompose, MaquinaVirtual
class GestionActivacionMaquinas(UserCreationForm):

    class Meta:
        fields = ['maquina_id', 'estado', 'ya_existe']


class FotoPerfilForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ['foto_perfil']
    submit_button = forms.CharField(widget=forms.HiddenInput(), initial='photo_submit')