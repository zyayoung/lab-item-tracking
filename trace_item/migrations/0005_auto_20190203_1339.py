# Generated by Django 2.1.5 on 2019-02-03 13:39

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trace_item', '0004_auto_20190203_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemlog',
            name='extra_data_to',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='属性'),
        ),
    ]
