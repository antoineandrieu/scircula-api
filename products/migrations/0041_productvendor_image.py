# Generated by Django 3.2.3 on 2021-05-24 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0040_auto_20210316_0938'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvendor',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
