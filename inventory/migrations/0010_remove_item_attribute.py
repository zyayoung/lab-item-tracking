# Generated by Django 2.1.5 on 2019-02-03 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_auto_20190202_1945'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='attribute',
        ),
    ]
