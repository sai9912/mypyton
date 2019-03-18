# Generated by Django 2.0.1 on 2018-07-12 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member_organisations', '0027_auto_20180712_0845'),
    ]

    operations = [
        migrations.RenameField(
            model_name='memberorganisation',
            old_name='gs1_cloud_ip_gln',
            new_name='gs1_cloud_ds_gln',
        ),
        migrations.AlterField(
            model_name='memberorganisation',
            name='gs1_cloud_ds_gln',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='GS1_CLOUD_DS_GLN'),
        ),
        migrations.AddField(
            model_name='memberorganisation',
            name='gs1_cloud_endpoint',
            field=models.CharField(blank=True, default='https://cloud.stg.gs1.org/api/v1/', max_length=100, verbose_name='GS1_CLOUD_ENDPOINT'),
        ),
    ]