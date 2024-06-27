# Generated by Django 3.1.7 on 2021-04-14 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0040_auto_20210316_0938'),
        ('customers', '0018_customeranalytic_product_size_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeranalytic',
            name='product_vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='products.productvendor'),
        ),
    ]
