# Generated by Django 3.2.12 on 2024-02-01 16:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0019_auto_20240201_1748'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaquinaDocker',
            fields=[
                ('maquinavulnerable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gestion.maquinavulnerable')),
                ('imagen_docker', models.CharField(max_length=255)),
                ('puerto_exposicion', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'Maquinas Docker',
            },
            bases=('gestion.maquinavulnerable',),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_inicial',
            field=models.CharField(default='f2c73fdda76a04ef93102ad8', max_length=25),
        ),
        migrations.AlterField(
            model_name='maquinavulnerable',
            name='bandera_usuario_root',
            field=models.CharField(default='a9f13d7b843c94432e632c3d', max_length=25),
        ),
    ]