# Generated by Django 3.0.6 on 2020-05-29 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0005_vendor_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='url',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
