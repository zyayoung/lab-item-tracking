# Generated by Django 2.1.5 on 2019-01-15 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
        ('inventory', '0005_auto_20190115_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='allowed_users',
            field=models.ManyToManyField(default='', to='login.User', verbose_name='允许用户'),
        ),
    ]
