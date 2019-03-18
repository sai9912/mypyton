# Generated by Django 2.0.1 on 2018-04-16 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=2)),
            ],
            options={
                'verbose_name_plural': 'Countries',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='LanguageByCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default', models.BooleanField(default=False)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BCM.Country')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BCM.Language')),
            ],
            options={
                'verbose_name_plural': 'Languages by countries',
            },
        ),
    ]
