# Generated by Django 3.2.5 on 2021-07-26 13:04

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_orderline_vendor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 26, 13, 4, 32, 594521, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 26, 13, 4, 32, 594543, tzinfo=utc)),
        ),
    ]
