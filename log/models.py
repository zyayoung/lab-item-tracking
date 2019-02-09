from django.db import models
from login.models import User as myUser

# Create your models here.

class Log(models.Model):
    operator = models.ForeignKey(
        myUser,
        verbose_name='操作人',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    time = models.DateTimeField('操作时间', auto_now_add=True)
    _id = models.IntegerField(
        verbose_name='ID',
        default=0,
    )
    category = models.TextField(
        verbose_name='类型',
        blank=True,
        null=True,
    )
    attribute = models.TextField(
        verbose_name='属性',
        blank=True,
        null=True,
    )
    _from = models.TextField(
        verbose_name='操作前',
        blank=True,
        null=True,
    )
    _to = models.TextField(
        verbose_name='操作后',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-time']
        verbose_name = "日志"
        verbose_name_plural = verbose_name