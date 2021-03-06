# Generated by Django 2.1.4 on 2019-02-02 08:32

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_item_is_property'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='item',
            name='unit',
        ),
        migrations.AddField(
            model_name='item',
            name='related_items',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='关联物品'),
        ),
        migrations.AddField(
            model_name='itemtemplate',
            name='key_name',
            field=models.CharField(default='名称', max_length=32, verbose_name='关键字段名称'),
        ),
    ]
