# Generated by Django 2.1.4 on 2019-01-14 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=32, unique=True, verbose_name='路径')),
                ('item', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.Item', verbose_name='物品')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parentPath', to='inventory.Location', verbose_name='父位置')),
            ],
            options={
                'verbose_name': '位置',
                'verbose_name_plural': '位置',
            },
        ),
    ]