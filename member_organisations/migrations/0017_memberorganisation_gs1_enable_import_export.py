# Generated by Django 2.0.1 on 2018-05-28 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member_organisations', '0016_auto_20180527_0917'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberorganisation',
            name='gs1_enable_import_export',
            field=models.BooleanField(default=False),
        ),
    ]
