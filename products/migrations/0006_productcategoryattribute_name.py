# Generated by Django 3.0.4 on 2020-03-13 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20200313_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategoryattribute',
            name='name',
            field=models.CharField(default='waist', max_length=64),
            preserve_default=False,
        ),
    ]
