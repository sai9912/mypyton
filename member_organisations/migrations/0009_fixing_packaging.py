# Generated by Django 2.0.1 on 2018-05-10 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member_organisations', '0008_merge_20180504_2034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productpackaging',
            name='package_level',
        ),
        migrations.RemoveField(
            model_name='productpackaging',
            name='package_type',
        ),
        migrations.AddField(
            model_name='productpackaging',
            name='code',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='ui_field_validation_callable',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='UI field validation callable'),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='ui_form_validation_callable',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='UI form validation callable'),
        ),
    ]