# Generated by Django 2.1.5 on 2019-02-02 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_auto_20190202_0832'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='is_property',
        ),
        migrations.AddField(
            model_name='itemtemplate',
            name='is_property',
            field=models.BooleanField(default=False, verbose_name='不可存入'),
        ),
    ]
