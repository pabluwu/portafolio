# Generated by Django 3.2.7 on 2021-12-02 02:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('process', '0004_tarea_tarea_subordinada'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tarea',
            old_name='tarea_subordinada',
            new_name='tarea_parent',
        ),
    ]