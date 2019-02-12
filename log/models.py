from django.db import models
from login.models import User as myUser
from django.utils.html import escape
from inventory.models import *
import re

from django.shortcuts import resolve_url


class Log(models.Model):
    operator = models.ForeignKey(
        myUser,
        verbose_name='操作人',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    time = models.DateTimeField('操作时间', auto_now_add=True)
    obj_id = models.IntegerField(
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
    before = models.TextField(
        verbose_name='操作前',
        blank=True,
        null=True,
    )
    after = models.TextField(
        verbose_name='操作后',
        blank=True,
        null=True,
    )

    def obj_url(self):
        if self.category == '物品' or self.category == '物品属性':
            return resolve_url('inventory:item', self.obj_id)
        elif self.category == '模板':
            return resolve_url('inventory:template', self.obj_id)
        elif self.category == '位置':
            return resolve_url('inventory:location', self.obj_id)
        elif self.category == '用户':
            return resolve_url('personal:user', self.obj_id)

    def obj(self):
        try:
            if self.category == '物品' or self.category == '物品属性':
                return Item.objects.get(id=self.obj_id)
            elif self.category == '模板':
                return ItemTemplate.objects.get(id=self.obj_id)
            elif self.category == '位置':
                return Location.objects.get(id=self.obj_id)
            elif self.category == '用户':
                return myUser.objects.get(id=self.obj_id)
        except:
            return '已删除'

    def get_html(self, name):
        html = name
        id = re.search(r'^id__(\d+)$', name)
        if id and id[1] != 0:
            try:
                id = id[1]
                item = Item.objects.get(id=id)
                html = '<a href="' + resolve_url('inventory:item', item.id) + '">' + escape(item.name) + '</a>'
            except KeyError as e:
                pass
        return html

    def get_before_html(self):
        return self.get_html(self.before)

    def get_after_html(self):
        return self.get_html(self.after)

    class Meta:
        ordering = ['-time']
        verbose_name = "日志"
        verbose_name_plural = verbose_name
