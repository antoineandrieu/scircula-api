# Generated by Django 3.0.4 on 2020-03-11 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        ('customers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vendors', '0002_auto_20200311_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeranalytic',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='products.Product'),
        ),
        migrations.AddField(
            model_name='customeranalytic',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='products.Size'),
        ),
        migrations.AddField(
            model_name='customer',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customer',
            name='vendor',
            field=models.ManyToManyField(to='vendors.Vendor'),
        ),
    ]
