# Generated by Django 2.0.1 on 2018-05-12 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='enable_leading',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='uid',
            field=models.CharField(default='', max_length=124, null=True),
        ),
    ]
