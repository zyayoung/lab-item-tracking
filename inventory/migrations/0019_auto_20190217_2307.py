# Generated by Django 2.1.5 on 2019-02-17 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_idcache'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idcache',
            name='pattern',
            field=models.CharField(max_length=256, verbose_name='模式'),
        ),
    ]
