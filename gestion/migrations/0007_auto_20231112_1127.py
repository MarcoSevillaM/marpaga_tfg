# Generated by Django 3.2.12 on 2023-11-12 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0006_auto_20231112_1124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jugador',
            name='nombre',
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='1b59a23ac04d8cd2f79c593e', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='f614970c67146f190725e9cc', max_length=25),
        ),
    ]
