# Generated by Django 3.1.3 on 2020-11-25 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0015_auto_20200811_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeranalytic',
            name='added_to_cart_product_title',
            field=models.TextField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='customeranalytic',
            name='purchased_product_title',
            field=models.TextField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='customeranalytic',
            name='purchased_size_id',
            field=models.TextField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='customeranalytic',
            name='size_added_to_cart_id',
            field=models.TextField(blank=True, default=False),
        ),
    ]
