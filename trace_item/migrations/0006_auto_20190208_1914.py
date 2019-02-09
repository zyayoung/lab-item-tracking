# Generated by Django 2.1.5 on 2019-02-08 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_auto_20190204_1111'),
        ('trace_item', '0005_auto_20190203_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemlog',
            name='location_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_from_here', to='inventory.Location', verbose_name='位置_从'),
        ),
        migrations.AlterField(
            model_name='itemlog',
            name='location_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_to_here', to='inventory.Location', verbose_name='位置_至'),
        ),
    ]