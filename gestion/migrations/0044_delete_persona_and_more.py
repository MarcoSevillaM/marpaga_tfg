# Generated by Django 5.0.2 on 2024-02-22 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0043_alter_persona_options_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Persona',
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='04284ee7b6e940356242611f', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='70ef4cfa598166b9270ed5b7', max_length=25),
        ),
    ]
