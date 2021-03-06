# Generated by Django 2.0.1 on 2018-05-15 09:57

from django.db import migrations, models
import products.helpers.product_helper


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_productimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(upload_to=products.helpers.product_helper.image_upload_directory, verbose_name='Image'),
        ),
    ]
