# Generated by Django 2.1.4 on 2019-01-29 15:24

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='名称')),
                ('quantity', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='数量')),
                ('unit', models.CharField(blank=True, default='', max_length=32, verbose_name='单位')),
                ('attribute', models.TextField(blank=True, verbose_name='属性')),
                ('extra_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='扩展数据')),
                ('is_public', models.BooleanField(default=False, verbose_name='公开')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='update_time')),
                ('allowed_users', models.ManyToManyField(blank=True, to='login.User', verbose_name='白名单')),
            ],
            options={
                'verbose_name': '物品',
                'verbose_name_plural': '物品',
                'ordering': ['-update_time'],
            },
        ),
        migrations.CreateModel(
            name='ItemTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='模块ID')),
                ('extra_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='扩展数据')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='create_time')),
            ],
            options={
                'verbose_name': '模块配置',
                'verbose_name_plural': '模块配置',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=32, verbose_name='路径')),
                ('is_public', models.BooleanField(default=False, verbose_name='公开')),
                ('allowed_users', models.ManyToManyField(blank=True, default='', to='login.User', verbose_name='白名单')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_children', to='inventory.Location', verbose_name='父位置')),
            ],
            options={
                'verbose_name': '位置',
                'verbose_name_plural': '位置',
            },
        ),
        migrations.CreateModel(
            name='LocationPermissionApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('explanation', models.CharField(blank=True, default='', max_length=256, verbose_name='申请理由')),
                ('approved', models.BooleanField(default=False, verbose_name='是否同意')),
                ('rejected', models.BooleanField(default=False, verbose_name='是否拒绝')),
                ('time', models.DateTimeField(auto_now=True, verbose_name='申请时间')),
                ('applicant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_apply', to='login.User', verbose_name='申请人')),
                ('auditor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_audit', to='login.User', verbose_name='处理人')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.Location', verbose_name='申请位置')),
            ],
            options={
                'verbose_name': '位置申请',
                'verbose_name_plural': '位置申请',
                'ordering': ['-time'],
            },
        ),
        migrations.AddField(
            model_name='item',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_item', to='inventory.Location', verbose_name='位置'),
        ),
        migrations.AddField(
            model_name='item',
            name='owner',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_item', to='login.User', verbose_name='所有者'),
        ),
        migrations.AddField(
            model_name='item',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='itemtemplate_instance', to='inventory.ItemTemplate', verbose_name='扩展数据模板'),
        ),
    ]
