# Generated by Django 3.1.7 on 2021-04-14 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0040_auto_20210316_0938'),
        ('customers', '0017_auto_20201125_0559'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeranalytic',
            name='product_size_vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='products.productsizevendor'),
        ),
    ]
