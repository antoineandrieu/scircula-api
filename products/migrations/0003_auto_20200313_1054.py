# Generated by Django 3.0.4 on 2020-03-13 10:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20200313_1040'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('stretch', models.IntegerField()),
                ('bust', models.FloatField()),
                ('waist', models.FloatField()),
                ('hips', models.FloatField()),
                ('thigh', models.FloatField()),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='type',
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='products.ProductCategory', to_field='name'),
        ),
    ]
