# Generated by Django 2.1.1 on 2019-01-27 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_auto_20190126_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='staff',
            field=models.ManyToManyField(blank=True, related_name='user_manager', to='login.User', verbose_name='被管理员工'),
        ),
    ]