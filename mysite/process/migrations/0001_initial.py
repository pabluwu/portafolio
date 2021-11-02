# Generated by Django 3.2.7 on 2021-11-02 19:29

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CalculoEstado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaActualCalculo', models.DateField(auto_now_add=True)),
                ('diasRestantes', models.DurationField(default=datetime.timedelta(0))),
            ],
        ),
        migrations.CreateModel(
            name='MotivoRechazo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
                ('respondido', models.BooleanField(default=False)),
                ('fechaCreacion', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.TextField()),
                ('realizado', models.BooleanField(default=False)),
                ('fechaCreacion', models.DateField(auto_now_add=True)),
                ('fechaLimite', models.DateField(default=datetime.datetime.now)),
                ('fechaTermino', models.DateField(default=datetime.datetime.now)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Semaforo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estadoSemaforo', models.CharField(max_length=2, null=True)),
                ('semaforoRojo', models.DurationField(default=datetime.timedelta(0))),
                ('calculoEstado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='process.calculoestado')),
            ],
        ),
        migrations.CreateModel(
            name='RespuestaRechazo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respuesta', models.TextField(null=True)),
                ('fechaRespuesta', models.DateField(auto_now_add=True)),
                ('aceptado', models.BooleanField(default=False)),
                ('motivoRechazo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='process.motivorechazo')),
            ],
        ),
        migrations.AddField(
            model_name='motivorechazo',
            name='tarea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='process.tarea'),
        ),
        migrations.AddField(
            model_name='motivorechazo',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='FlujoTarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('tareas', models.ManyToManyField(to='process.Tarea')),
            ],
        ),
        migrations.AddField(
            model_name='calculoestado',
            name='tarea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='process.tarea'),
        ),
    ]
