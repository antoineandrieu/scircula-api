# Generated by Django 3.0.8 on 2020-07-31 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0012_auto_20200731_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeranalytic',
            name='added_to_cart',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='customeranalytic',
            name='purchased',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
