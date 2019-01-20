# Generated by Django 2.1.1 on 2019-01-20 03:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_auto_20190120_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='allowed_users',
            field=models.ManyToManyField(blank=True, to='login.User', verbose_name='允许用户'),
        ),
        migrations.AlterField(
            model_name='item',
            name='owner',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='login.User', verbose_name='所有者'),
        ),
    ]
