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
        #Cuando recibo la foto_perfil la tramito para que el nombre de la foto sea "nombreUsuario.jpg"
        def save(self, commit=True):
            user = super(FotoPerfilForm, self).save(commit=False)
            user.foto_perfil = self.cleaned_data['foto_perfil']
            if commit:
                user.save()
            return user