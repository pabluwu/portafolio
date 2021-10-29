# Generated by Django 3.2.7 on 2021-10-12 06:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process', '0004_alter_tarea_fechatermino'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarea',
            name='fechaLimite',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='tarea',
            name='fechaTermino',
            field=models.DateTimeField(default=None),
        ),
    ]
