# Generated by Django 3.0.4 on 2020-03-13 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20200313_1054'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productcategory',
            name='bust',
        ),
        migrations.RemoveField(
            model_name='productcategory',
            name='hips',
        ),
        migrations.RemoveField(
            model_name='productcategory',
            name='stretch',
        ),
        migrations.RemoveField(
            model_name='productcategory',
            name='thigh',
        ),
        migrations.RemoveField(
            model_name='productcategory',
            name='waist',
        ),
        migrations.CreateModel(
            name='ProductCategoryAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stretch', models.IntegerField()),
                ('bust', models.FloatField()),
                ('waist', models.FloatField()),
                ('hips', models.FloatField()),
                ('thigh', models.FloatField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='products.ProductCategory')),
            ],
        ),
    ]
