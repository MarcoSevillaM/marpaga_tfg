# Generated by Django 3.2.12 on 2024-02-01 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0028_auto_20240202_0038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='a4421e32bc810528ca99412d', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='5275374cd5be04a5783708ac', max_length=25),
        ),
    ]
