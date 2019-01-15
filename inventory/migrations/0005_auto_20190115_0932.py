# Generated by Django 2.1.5 on 2019-01-15 01:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_auto_20190115_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location', to='inventory.Location', verbose_name='位置'),
        ),
    ]
