# Generated by Django 3.0.6 on 2020-05-29 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0004_remove_vendor_valid_till'),
        ('customers', '0010_auto_20200528_1256'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='vendor',
        ),
        migrations.AddField(
            model_name='customer',
            name='vendors',
            field=models.ManyToManyField(blank=True, related_name='customers', to='vendors.Vendor'),
        ),
    ]
