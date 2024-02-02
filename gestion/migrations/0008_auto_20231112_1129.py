# Generated by Django 3.2.12 on 2023-11-12 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0007_auto_20231112_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='332d369be8750f562fc59542', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='352dfe6b61d7abd4b4154262', max_length=25),
        ),
        migrations.CreateModel(
            name='MaquinaJugador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activa', models.BooleanField(default=False)),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.jugador')),
                ('maquina_vulnerable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion.maquinavulnerable')),
            ],
        ),
    ]
