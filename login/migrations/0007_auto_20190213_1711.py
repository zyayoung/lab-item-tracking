# Generated by Django 2.1.1 on 2019-02-13 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0006_auto_20190213_1700'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='last_online_time',
            new_name='latest_online_time',
        ),
    ]