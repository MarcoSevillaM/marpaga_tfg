# Generated by Django 3.2.12 on 2023-11-12 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0014_auto_20231112_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='8b3d7406fddc9b4678d97287', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='48468dcd09344079dd86cb58', max_length=25),
        ),
    ]
