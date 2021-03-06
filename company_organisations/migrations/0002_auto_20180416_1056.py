# Generated by Django 2.0.1 on 2018-04-16 10:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('member_organisations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company_organisations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyorganisation',
            name='member_organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='companies', to='member_organisations.MemberOrganisation'),
        ),
        migrations.AddField(
            model_name='companyorganisation',
            name='users',
            field=models.ManyToManyField(related_name='company_organisations_companyorganisation', through='company_organisations.CompanyOrganisationUser', to=settings.AUTH_USER_MODEL),
        ),
    ]
