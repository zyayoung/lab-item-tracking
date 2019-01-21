# Generated by Django 2.1.4 on 2019-01-21 06:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
        ('inventory', '0003_auto_20190120_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpermissionapplication',
            name='auditor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auditor', to='login.User', verbose_name='批准人'),
        ),
        migrations.AlterField(
            model_name='locationpermissionapplication',
            name='applicant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applicant', to='login.User', verbose_name='申请人'),
        ),
    ]
