# Generated by Django 2.1.4 on 2019-02-01 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_auto_20190131_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_property',
            field=models.BooleanField(default=False, verbose_name='非物品'),
        ),
    ]