# Generated by Django 3.2.7 on 2021-10-21 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process', '0011_auto_20211020_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='motivorechazo',
            name='solucionado',
            field=models.BooleanField(default=False),
        ),
    ]