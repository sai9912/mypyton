# Generated by Django 2.0.1 on 2018-07-12 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member_organisations', '0026_memberorganisation_simplified_barcode_generation'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberorganisation',
            name='gs1_dashboard_label',
            field=models.CharField(default='GS1 Dashboard', max_length=100),
        ),
        migrations.AddField(
            model_name='memberorganisation',
            name='gs1_dashboard_url',
            field=models.CharField(default='https://www.gs1.org/services/activate', max_length=100),
        ),
    ]