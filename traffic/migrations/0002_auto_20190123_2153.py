# Generated by Django 2.1.5 on 2019-01-23 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('traffic', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='traffic',
            old_name='datatime',
            new_name='datetime',
        ),
    ]