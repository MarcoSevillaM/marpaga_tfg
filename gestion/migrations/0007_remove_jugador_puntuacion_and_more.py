# Generated by Django 5.0.2 on 2024-03-17 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0006_alter_maquinavulnerable_bandera_usuario_inicial_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jugador',
            name='puntuacion',
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='c5453abf172a33d4e2825cc5', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='985298e4933d16215384aa7d', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='nivel_dificultad',
            field=models.CharField(choices=[('Facil', 'Facil'), ('Media', 'Media'), ('Dificil', 'Dificil'), ('Experta', 'Experta')], max_length=10),
        ),
    ]
