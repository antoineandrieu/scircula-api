# Generated by Django 3.2.7 on 2021-09-24 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0028_alter_vendor_uninstalled_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='fmf_loaded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='fmf_unloaded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
