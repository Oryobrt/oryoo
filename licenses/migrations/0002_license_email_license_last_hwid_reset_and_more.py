# Generated by Django 5.2 on 2025-05-03 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licenses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='last_hwid_reset',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='license',
            name='activated_on',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='license',
            name='hwid',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='license',
            name='license_key',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
