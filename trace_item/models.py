from django.db import models
from django.utils import timezone
from login.models import User as myUser
from inventory.models import Location


class ItemLog(models.Model):
    operator = models.ForeignKey(myUser, verbose_name='操作人', null=True, blank=True, on_delete=models.SET_NULL)
    time = models.DateTimeField('操作时间', default=timezone.now)
    location_from = models.ForeignKey(Location, verbose_name='从', related_name='location_from', blank=True, null=True, on_delete=models.SET_NULL)
    quantity_from = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        blank=True,
        verbose_name="操作前数量"
    )
    location_to = models.ForeignKey(Location, verbose_name='到', related_name='location_to', blank=True, null=True, on_delete=models.SET_NULL)
    quantity_to = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        blank=True,
        verbose_name="操作后数量"
    )

    def operation(self):
        ret = ''
        if self.location_to != self.location_from:
            ret += 'Position: {0} -> {1}'.format(self.location_from, self.location_to)
        if self.quantity_to != self.quantity_from:
            if ret:
                ret += ' | '
            ret += 'Quantity: {0} -> {1}'.format(self.quantity_from, self.quantity_to)

        return ret

    def __str__(self):
        ret = '{0}'.format(self.operator)
        if self.location_to != self.location_from:
            if ret:
                ret += ' | '
            ret += 'Pos: {0} -> {1}'.format(self.location_from, self.location_to)
        if self.quantity_to != self.quantity_from:
            if ret:
                ret += ' | '
            ret += 'Qua: {0} -> {1}'.format(self.quantity_from, self.quantity_to)

        return ret

    class Meta:
        ordering = ['time']
        verbose_name = "物品操作记录"
        verbose_name_plural = verbose_name
