# Generated by Django 3.2.7 on 2021-10-29 01:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('process', '0015_motivorechazo_respondido'),
    ]

    operations = [
        migrations.CreateModel(
            name='Semaforo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estadoSemaforo', models.CharField(max_length=1, null=True)),
                ('calculoEstado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='process.tarea')),
            ],
        ),
        migrations.CreateModel(
            name='CalculoEstado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaActualCalculo', models.DateField(auto_now_add=True)),
                ('diasRestantes', models.DurationField()),
                ('tarea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='process.tarea')),
            ],
        ),
    ]
