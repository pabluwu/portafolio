# Generated by Django 3.2.7 on 2021-10-12 07:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process', '0007_auto_20211012_0400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarea',
            name='fechaCreacion',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='tarea',
            name='fechaLimite',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='tarea',
            name='fechaTermino',
            field=models.DateField(default=None),
        ),
    ]
