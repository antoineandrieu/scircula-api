# Generated by Django 3.2.6 on 2021-09-13 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0022_vendor_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='button_loaded',
            field=models.BooleanField(default=False),
        ),
    ]
