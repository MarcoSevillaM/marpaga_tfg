# Generated by Django 3.2.12 on 2023-11-10 21:12

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gestion', '0003_rename_jugador_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jugador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel', models.IntegerField(default=0)),
                ('puntuacion', models.IntegerField(blank=True, default=0, null=True)),
                ('usr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MaquinaVulnerable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('nivel_dificultad', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)])),
                ('nivel_minimo', models.IntegerField()),
                ('bandera_usuario_inicial', models.CharField(max_length=255)),
                ('bandera_usuario_root', models.CharField(max_length=255)),
                ('identificador', models.CharField(blank=True, max_length=255, null=True)),
                ('activa', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ValoracionMaquina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valoracion', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.jugador')),
                ('maquina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.maquinavulnerable')),
            ],
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
