# Generated by Django 2.1.1 on 2019-01-27 14:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_auto_20190127_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_item', to='inventory.Location', verbose_name='位置'),
        ),
        migrations.AlterField(
            model_name='item',
            name='owner',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_item', to='login.User', verbose_name='所有者'),
        ),
        migrations.AlterField(
            model_name='location',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='location_children', to='inventory.Location', verbose_name='父位置'),
        ),
        migrations.AlterField(
            model_name='locationpermissionapplication',
            name='applicant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_apply', to='login.User', verbose_name='申请人'),
        ),
        migrations.AlterField(
            model_name='locationpermissionapplication',
            name='auditor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_audit', to='login.User', verbose_name='处理人'),
        ),
    ]