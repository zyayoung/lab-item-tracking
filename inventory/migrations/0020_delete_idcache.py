# Generated by Django 2.1.5 on 2019-02-18 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_auto_20190217_2307'),
    ]

    operations = [
        migrations.DeleteModel(
            name='IdCache',
        ),
    ]