# Generated by Django 5.0.2 on 2024-03-09 18:18

import django.db.models.deletion
import gestion.functions
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MaquinaVulnerable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('nivel_dificultad', models.CharField(choices=[('Facil', 'Facil'), ('Medio', 'Medio'), ('Dificl', 'Dificil'), ('Bestia', 'Bestia')], max_length=6)),
                ('puntuacion_minima_activacion', models.IntegerField(default=0)),
                ('descripcion', models.TextField(blank=True, max_length=255, null=True)),
                ('bandera_usuario_inicial', models.CharField(default='8d28c1e47ddba0a77b3b0230', max_length=25)),
                ('bandera_usuario_root', models.CharField(default='84faf9aa4514de833d153f26', max_length=25)),
                ('instrucciones', models.TextField(default='', max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Maquinas vulnerables',
            },
        ),
        migrations.CreateModel(
            name='Jugador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntuacion', models.IntegerField(default=0)),
                ('foto_perfil', models.ImageField(blank=True, default='photoPersonal/default.jpg', null=True, storage=gestion.functions.OverwriteStorage(), upload_to='photoPersonal/')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Jugadores',
            },
        ),
        migrations.CreateModel(
            name='MaquinaDocker',
            fields=[
                ('maquinavulnerable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gestion.maquinavulnerable')),
                ('archivo', models.FileField(blank=True, null=True, upload_to='archivoZipDocker/', validators=[gestion.functions.Validate_zip_file])),
            ],
            options={
                'verbose_name_plural': 'Máquinas Docker',
            },
            bases=('gestion.maquinavulnerable',),
        ),
        migrations.CreateModel(
            name='MaquinaDockerCompose',
            fields=[
                ('maquinavulnerable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gestion.maquinavulnerable')),
                ('archivo', models.FileField(blank=True, upload_to='archivoZipDockerCompose/', validators=[gestion.functions.Validate_zip_file])),
            ],
            options={
                'verbose_name_plural': 'Maquinas Docker Compose',
            },
            bases=('gestion.maquinavulnerable',),
        ),
        migrations.CreateModel(
            name='MaquinaVirtual',
            fields=[
                ('maquinavulnerable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gestion.maquinavulnerable')),
                ('ip_maquina_virtual', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name_plural': 'Maquinas Virtuales',
            },
            bases=('gestion.maquinavulnerable',),
        ),
        migrations.CreateModel(
            name='MaquinaJugador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activa', models.BooleanField(default=False)),
                ('ip_address', models.CharField(blank=True, max_length=15, null=True)),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.jugador')),
                ('maquina_vulnerable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.maquinavulnerable')),
            ],
            options={
                'verbose_name_plural': 'Relaciones jugadores con maquinas',
            },
        ),
        migrations.CreateModel(
            name='PuntuacionJugador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntuacion', models.IntegerField(default=0)),
                ('fecha_obtencion', models.DateTimeField(auto_now_add=True)),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.jugador')),
                ('maquina_vulnerable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.maquinavulnerable')),
            ],
            options={
                'verbose_name_plural': 'Banderas de los jugadores',
            },
        ),
    ]
