from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0026_auto_20201126_0921"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="product",
            unique_together=set(),
        ),
        migrations.AlterModelTable(
            name="productvendor",
            table="product_vendor",
        ),
        migrations.RemoveField(
            model_name="product",
            name="external_id",
        ),
    ]
