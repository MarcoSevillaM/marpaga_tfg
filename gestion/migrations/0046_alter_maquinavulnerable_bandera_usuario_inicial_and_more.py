# Generated by Django 5.0.2 on 2024-02-27 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0045_remove_maquinadocker_puerto_exposicion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='6c3735dd145401011e7b1b4b', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='1c29eff4cb34ed09dff7b99b', max_length=25),
        ),
    ]