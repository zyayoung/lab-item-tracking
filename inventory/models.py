# -*- coding: utf-8 -*-
# -*- mode: python -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from login.models import User as myUser
import datetime


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
    is_public = models.BooleanField(default=False, verbose_name='公开')
    allowed_users = models.ManyToManyField(
        myUser,
        blank=True,
        default='',
        verbose_name="白名单",
    )

    def allowed_users_summary(self):
        return ' '.join([user.name for user in self.allowed_users.all()[:5]]) + \
               ('' if self.allowed_users.count() <= 5 else ' 等%d人' % self.allowed_users.count())

    def __str__(self):
        path_list = [self.path]
        p = self.parent
        while p:
            path_list.insert(0, p.path)
            p = p.parent
        return '-'.join(path_list)

    class Meta:
        verbose_name = "位置"
        verbose_name_plural = verbose_name


class Item(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")
    quantity = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        blank=True,
        verbose_name="数量",
    )
    unit = models.CharField(max_length=32, default='', verbose_name="单位")
    attribute = models.TextField(blank=True, verbose_name="属性")
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="位置",
        related_name="location",
    )
    owner = models.ForeignKey(
        myUser,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="所有者",
        related_name="owner",
    )
    is_public = models.BooleanField(default=False, verbose_name='公开')
    allowed_users = models.ManyToManyField(
        myUser,
        blank=True,
        verbose_name="白名单",
    )
    update_time = models.DateTimeField("update_time", auto_now=True)

    def __str__(self):
        return "{0}".format(self.name)

    class Meta:
        ordering = ['-update_time']
        verbose_name = "物品"
        verbose_name_plural = verbose_name


class LocationPermissionApplication(models.Model):
    applicant = models.ForeignKey(
        myUser,
        verbose_name='申请人',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    location = models.ForeignKey(
        Location,
        verbose_name='申请位置',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    explanation = models.CharField(
        max_length=256,
        default='',
        verbose_name='申请理由',
    )
    approved = models.BooleanField(default=False, verbose_name='是否同意')
    rejected = models.BooleanField(default=False, verbose_name='是否拒绝')
    time = models.DateTimeField(auto_now=True, verbose_name='申请时间')

    class Meta:
        ordering = ['-time']
        verbose_name = "位置申请"
        verbose_name_plural = verbose_name
