# Generated by Django 2.1.5 on 2019-01-30 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20190130_1046'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='locationpermissionapplication',
            options={'ordering': ['-closed'], 'verbose_name': '位置申请', 'verbose_name_plural': '位置申请'},
        ),
        migrations.AddField(
            model_name='locationpermissionapplication',
            name='closed',
            field=models.BooleanField(default=False, verbose_name='是否拒绝'),
        ),
    ]
