# Generated by Django 3.1 on 2020-08-11 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_auto_20200624_0827'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='inseam',
            field=models.BooleanField(default=False),
        ),
    ]
