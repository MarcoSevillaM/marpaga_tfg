# Generated by Django 3.2.12 on 2024-02-01 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0023_auto_20240201_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='177cd78692d7297e92bcbeff', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='4ff43ffa3c6b96973347f39a', max_length=25),
        ),
    ]
