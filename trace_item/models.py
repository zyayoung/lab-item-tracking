from django.db import models
from django.utils import timezone
from login.models import User as myUser
from inventory.models import Location, Item
from django.contrib.postgres.fields import JSONField


class ItemLog(models.Model):
    operator = models.ForeignKey(
        myUser,
        verbose_name='操作人',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    time = models.DateTimeField('操作时间', auto_now_add=True)
    item = models.ForeignKey(
        Item,
        verbose_name='物品',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    extra_data_to = JSONField(
        default=dict,
        blank=True,
        verbose_name="属性",
    )
    location_to = models.ForeignKey(
        Location,
        verbose_name='位置',
        related_name='location_to_here',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ['-time']
        verbose_name = "物品操作记录"
        verbose_name_plural = verbose_name
