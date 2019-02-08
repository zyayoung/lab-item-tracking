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
    location_from = models.ForeignKey(
        Location,
        verbose_name='位置_从',
        related_name='location_from_here',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    location_to = models.ForeignKey(
        Location,
        verbose_name='位置_至',
        related_name='location_to_here',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def is_location(self):
        return self.location_to

    def operation(self):
        return '位置' if self.is_location() else '属性'

    def to(self):
        return self.location_to if self.is_location() else ''

    class Meta:
        ordering = ['-time']
        verbose_name = "物品操作记录"
        verbose_name_plural = verbose_name
