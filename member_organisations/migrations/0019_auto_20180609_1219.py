# Generated by Django 2.0.1 on 2018-06-09 12:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('member_organisations', '0018_auto_20180605_1140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productattribute',
            old_name='definition',
            new_name='definition_i18n',
        ),
    ]
