# Generated by Django 2.0.1 on 2018-07-05 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member_organisations', '0025_auto_20180630_0819'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberorganisation',
            name='simplified_barcode_generation',
            field=models.BooleanField(default=True),
        ),
    ]