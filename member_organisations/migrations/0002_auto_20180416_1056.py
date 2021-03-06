# Generated by Django 2.0.1 on 2018-04-16 10:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('member_organisations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('knox', '0006_auto_20160818_0932'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttemplate',
            name='package_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.PackageLevel'),
        ),
        migrations.AddField(
            model_name='productpackaging',
            name='member_organisation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_packaging', to='member_organisations.MemberOrganisation'),
        ),
        migrations.AddField(
            model_name='productpackaging',
            name='package_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.PackageLevel'),
        ),
        migrations.AddField(
            model_name='productpackaging',
            name='package_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.PackageType'),
        ),
        migrations.AddField(
            model_name='memberorganisationuser',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organization_users', to='member_organisations.MemberOrganisation'),
        ),
        migrations.AddField(
            model_name='memberorganisationuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_organisations_memberorganisationuser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='memberorganisationowner',
            name='organization',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='member_organisations.MemberOrganisation'),
        ),
        migrations.AddField(
            model_name='memberorganisationowner',
            name='organization_user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='member_organisations.MemberOrganisationUser'),
        ),
        migrations.AddField(
            model_name='memberorganisation',
            name='users',
            field=models.ManyToManyField(related_name='member_organisations_memberorganisation', through='member_organisations.MemberOrganisationUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='m2mtoken',
            name='token',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='m2m_tokens', to='knox.AuthToken'),
        ),
    ]
