# Generated by Django 3.2.12 on 2024-02-01 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0029_auto_20240202_0040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquinadockercompose',
            name='extracted_folder',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='fb8c9d562795282de73637f5', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='dc1d2fbee2c00b3aa2316f2b', max_length=25),
        ),
    ]