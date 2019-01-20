# Generated by Django 2.1.5 on 2019-01-20 04:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0007_auto_20190120_1117'),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='操作时间')),
                ('quantity_from', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='操作前数量')),
                ('quantity_to', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='操作后数量')),
                ('location_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_from', to='inventory.Location', verbose_name='从')),
                ('location_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_to', to='inventory.Location', verbose_name='到')),
                ('operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='login.User', verbose_name='操作人')),
            ],
            options={
                'verbose_name': '物品操作记录',
                'verbose_name_plural': '物品操作记录',
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='LocationPermissionApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('explanation', models.CharField(default='', max_length=256, verbose_name='申请理由')),
                ('approved', models.BooleanField(default=False, verbose_name='是否同意')),
                ('rejected', models.BooleanField(default=False, verbose_name='是否拒绝')),
                ('time', models.DateTimeField(auto_now=True, verbose_name='申请时间')),
                ('applicant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='login.User', verbose_name='申请人')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.Location', verbose_name='申请位置')),
            ],
            options={
                'verbose_name': '位置申请',
                'verbose_name_plural': '位置申请',
                'ordering': ['time'],
            },
        ),
    ]
