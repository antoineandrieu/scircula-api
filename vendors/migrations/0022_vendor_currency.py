# Generated by Django 3.2.6 on 2021-08-04 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0021_visit_returning'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='currency',
            field=models.CharField(default='EUR', max_length=3),
        ),
    ]
