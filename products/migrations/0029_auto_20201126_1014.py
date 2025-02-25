# Generated by Django 3.1.3 on 2020-11-26 10:14

from django.db import migrations


def make_many_vendors(apps, schema_editor):
    """
    Create the ProductSizeVendor Objects with vendor and product size as foreign key
    and external_id field
    """
    ProductSize = apps.get_model("products", "ProductSize")
    ProductSizeVendor = apps.get_model("products", "ProductSizeVendor")

    for product_size in ProductSize.objects.all():
        product_size_vendor = ProductSizeVendor.objects.create(
            product_size=product_size,
            vendor=product_size.product.vendor,
            external_id=product_size.external_id,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0028_productsizevendor"),
    ]

    operations = [
        migrations.RunPython(make_many_vendors),
    ]
