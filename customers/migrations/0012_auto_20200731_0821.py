# Generated by Django 3.0.8 on 2020-07-31 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0011_auto_20200529_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeranalytic',
            name='added_to_cart',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customeranalytic',
            name='purchased',
            field=models.BooleanField(default=False),
        ),
    ]
