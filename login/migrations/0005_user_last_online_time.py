# Generated by Django 2.1.1 on 2019-02-13 16:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0004_user_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_online_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
