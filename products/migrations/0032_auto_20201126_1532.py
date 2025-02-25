# Generated by Django 3.1.3 on 2020-11-26 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0031_auto_20201126_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsizevendor',
            name='product_size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productsize'),
        ),
        migrations.AlterField(
            model_name='productvendor',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
    ]
