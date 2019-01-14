# -*- coding: utf-8 -*-
# -*- mode: python -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from login.models import User as myUser
import datetime


class Item(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")
    quantity = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        blank=True,
        verbose_name="数量")
    unit = models.CharField(max_length=32, default='', verbose_name="单位")
    attribute = models.TextField(blank=True, verbose_name="属性")
    user = models.ManyToManyField(myUser, default='', verbose_name="用户")

    def __str__(self):
        return "{0}".format(self.name)

    class Meta:
        ordering = ['id']
        verbose_name = "物品"
        verbose_name_plural = verbose_name


class Location(models.Model):
    path = models.CharField(max_length=32, verbose_name="路径")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="父位置",
        related_name="parentPath",
    )
    item = models.OneToOneField(
        Item,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="物品",
    )

    def __str__(self):
        path_list = [self.path]
        p = self.parent
        while p:
            path_list.insert(0, p.path)
            p = p.parent
        return '-'.join(path_list) # + (":" + self.item.name if self.item else "")

    class Meta:
        verbose_name = "位置"
        verbose_name_plural = verbose_name