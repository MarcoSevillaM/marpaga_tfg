# Generated by Django 5.0.2 on 2024-03-01 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0051_alter_maquinavulnerable_bandera_usuario_inicial_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='f676fd6f892230ff206c149d', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='a9cd758bedf3a42df3a95151', max_length=25),
        ),
    ]
