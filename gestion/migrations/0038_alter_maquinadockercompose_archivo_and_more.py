# Generated by Django 5.0.2 on 2024-02-19 12:36

import gestion.functions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0037_alter_maquinavulnerable_bandera_usuario_inicial_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquinadockercompose',
            name='archivo',
            field=models.FileField(upload_to='archivoZipDockerCompose/', validators=[gestion.functions.validate_zip_file]),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='3d2b9631e7786c1ee233bab3', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='71122074e99cc786ce6ffe4d', max_length=25),
        ),
    ]