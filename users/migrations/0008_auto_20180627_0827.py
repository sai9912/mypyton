# Generated by Django 2.0.1 on 2018-06-27 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20180612_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='member_organisation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='member_organisations.MemberOrganisation'),
        ),
    ]