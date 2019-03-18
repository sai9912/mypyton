# Generated by Django 2.0.1 on 2018-04-24 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('member_organisations', '0004_auto_20180420_0345'),
        ('products', '0005_auto_20180423_0943'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='packagetype',
            name='description',
        ),
        migrations.RemoveField(
            model_name='packagetype',
            name='type',
        ),
        migrations.AddField(
            model_name='packagetype',
            name='description_i18n',
            field=models.TextField(default='{}'),
        ),
        migrations.AddField(
            model_name='packagetype',
            name='member_organisation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='member_organisations.MemberOrganisation'),
        ),
        migrations.AddField(
            model_name='packagetype',
            name='type_i18n',
            field=models.TextField(default='{}'),
        ),
        migrations.AlterField(
            model_name='gtintargetmarket',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gtin_target_market', to='products.Product'),
        ),
    ]
