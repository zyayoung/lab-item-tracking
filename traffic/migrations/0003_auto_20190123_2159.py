# Generated by Django 2.1.5 on 2019-01-23 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('traffic', '0002_auto_20190123_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traffic',
            name='response_time',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=6, verbose_name='Response Time'),
        ),
    ]