# Generated by Django 3.2.6 on 2021-09-15 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0023_vendor_button_loaded'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='button_loaded',
        ),
        migrations.AddField(
            model_name='vendor',
            name='script_external_id',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
