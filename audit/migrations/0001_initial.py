# Generated by Django 2.0.1 on 2018-04-16 10:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CloudLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, null=True)),
                ('msg', models.TextField(null=True)),
                ('ref', models.CharField(max_length=50, null=True)),
                ('key', models.CharField(max_length=50, null=True)),
                ('gs1_cloud_last_rc', models.CharField(max_length=50, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logger', models.CharField(max_length=50, null=True)),
                ('level', models.CharField(max_length=10, null=True)),
                ('trace', models.TextField(null=True)),
                ('msg', models.TextField(null=True)),
                ('ip_address', models.CharField(max_length=15, null=True)),
                ('username', models.CharField(max_length=50, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]