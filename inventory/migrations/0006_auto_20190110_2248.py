# Generated by Django 2.1.1 on 2019-01-10 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_auto_20190110_2158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='size',
        ),
        migrations.AddField(
            model_name='material',
            name='quantity',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='数量'),
        ),
        migrations.AlterField(
            model_name='material',
            name='location',
            field=models.TextField(verbose_name='位置'),
        ),
        migrations.AlterField(
            model_name='material',
            name='name',
            field=models.CharField(max_length=128, verbose_name='名称'),
        ),
        migrations.AlterField(
            model_name='material',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.Unit', verbose_name='单位'),
        ),
        migrations.AlterField(
            model_name='unit',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
