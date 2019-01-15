# Generated by Django 2.1.5 on 2019-01-15 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_auto_20190115_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='user',
            field=models.ManyToManyField(default='', to='login.User', verbose_name='用户'),
        ),
        migrations.AlterField(
            model_name='location',
            name='allowed_users',
            field=models.ManyToManyField(blank=True, default='', to='login.User', verbose_name='允许用户'),
        ),
    ]
