# Generated by Django 2.1.5 on 2019-01-20 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20190120_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_public',
            field=models.BooleanField(default=False, verbose_name='公开'),
        ),
        migrations.AddField(
            model_name='location',
            name='is_public',
            field=models.BooleanField(default=False, verbose_name='公开'),
        ),
        migrations.AlterField(
            model_name='item',
            name='allowed_users',
            field=models.ManyToManyField(blank=True, to='login.User', verbose_name='白名单'),
        ),
        migrations.AlterField(
            model_name='location',
            name='allowed_users',
            field=models.ManyToManyField(blank=True, default='', to='login.User', verbose_name='白名单'),
        ),
    ]