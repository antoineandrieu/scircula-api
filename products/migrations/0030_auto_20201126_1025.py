# Generated by Django 3.1.3 on 2020-11-26 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_auto_20201126_1014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='vendor',
        ),
        migrations.RemoveField(
            model_name='productsize',
            name='external_id',
        ),
    ]
