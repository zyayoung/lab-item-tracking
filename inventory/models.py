# -*- coding: utf-8 -*-
# -*- mode: python -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import JSONField
from login.models import User as myUser
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    path = models.CharField(max_length=32, verbose_name=_("路径"))
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("父位置"),
        related_name="location_children",
    )
    is_public = models.BooleanField(default=False, verbose_name=_("公开"))
    allowed_users = models.ManyToManyField(
        myUser,
        blank=True,
        default='',
        verbose_name=_("白名单"),
    )

    def allowed_users_summary(self):
        return ' '.join([user.name for user in self.allowed_users.all()[:5]]) + \
               ('' if self.allowed_users.count() <= 5 else ' 等%d人' % self.allowed_users.count())

    def __str__(self):
        path_list = []
        loc = self
        while loc:
            path_list.insert(0, loc.path)
            loc = loc.parent
        return '-'.join(path_list)

    class Meta:
        verbose_name = _("位置")
        verbose_name_plural = verbose_name


class ItemTemplate(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_("模块名称"))
    key_name = models.CharField(
        max_length=32,
        default='名称',
        verbose_name=_("关键字段名称"),
    )
    key_name_placeholder = models.CharField(
        max_length=128,
        default='用于显示的名称',
        verbose_name=_("关键字段占位符"),
    )
    custom_id_name = models.CharField(
        max_length=128,
        default='ID',
        verbose_name="custom_id_name",
    )
    custom_id_format = models.CharField(
        max_length=128,
        default='%date%-%id%',
        verbose_name="custom_id_format",
    )
    extra_data = JSONField(default=dict, blank=True, verbose_name=_("扩展数据"))
    is_property = models.BooleanField(default=False, verbose_name=_("不可存入"))
    create_time = models.DateTimeField("create_time", auto_now_add=True)
    allowed_users = models.ManyToManyField(
        myUser,
        blank=True,
        verbose_name=_("白名单"),
    )

    def __str__(self):
        return self.name

    def allowed_users_summary(self):
        return '全部' if not self.allowed_users.exists() else ' '.join([user.name for user in self.allowed_users.all()[:5]]) + \
               ('' if self.allowed_users.count() <= 5 else ' 等%d人' % self.allowed_users.count())

    def category(self):
        return "物品属性" if self.is_property else "物品"

    def allowed_users_str(self):
        return '|'.join([user.name for user in self.allowed_users.all()])

    class Meta:
        ordering = ['-create_time']
        verbose_name = _("模板")
        verbose_name_plural = verbose_name


class Item(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("名称"))
    custom_id = models.CharField(
        max_length=128,
        verbose_name=_("自定编号"),
        null=True,
        blank=True,
    )
    template = models.ForeignKey(
        ItemTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("扩展数据模板"),
        related_name="itemtemplate_instance",
    )
    extra_data = JSONField(default=dict, blank=True, verbose_name=_("扩展数据"))
    related_items = JSONField(default=dict, blank=True, verbose_name=_("关联物品"))
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("位置"),
        related_name="location_item",
    )
    owner = models.ForeignKey(
        myUser,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("创建用户"),
        related_name="user_item",
    )
    is_public = models.BooleanField(default=False, verbose_name=_("公开"))
    allowed_users = models.ManyToManyField(
        myUser,
        blank=True,
        verbose_name=_("白名单"),
    )
    update_time = models.DateTimeField("update_time", auto_now=True)

    def __str__(self):
        return self.name

    def allowed_users_str(self):
        return '|'.join([user.name for user in self.allowed_users.all()])

    def del_permission(self, tmp_user):
        return self.owner == tmp_user or \
               tmp_user.staff.filter(id=self.owner.id).exists() or \
               tmp_user.is_superadmin  # User can delete item iff. he/she is super admin / owner / owner's manager

    def unlink_permission(self, tmp_user):
        return not self.del_permission(tmp_user) and \
               self.allowed_users.filter(id=tmp_user.id).exists()  # Otherwise, only directly linked user can unlink

    class Meta:
        ordering = ['-update_time']
        verbose_name = _("物品")
        verbose_name_plural = verbose_name


class LocationPermissionApplication(models.Model):
    applicant = models.ForeignKey(
        myUser,
        verbose_name=_("申请人"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_apply',
    )
    location = models.ForeignKey(
        Location,
        verbose_name=_("申请位置"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    explanation = models.CharField(
        max_length=256,
        default='',
        blank=True,
        verbose_name=_("申请理由"),
    )
    approved = models.BooleanField(default=False, verbose_name=_("是否同意"))
    rejected = models.BooleanField(default=False, verbose_name=_("是否拒绝"))
    closed = models.BooleanField(default=False, verbose_name=_("是否拒绝"))
    time = models.DateTimeField(auto_now=True, verbose_name=_("申请时间"))
    auditor = models.ForeignKey(
        myUser,
        verbose_name=_("处理人"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_audit',
    )

    def approve(self):
        self.approved = True
        self.closed = True

        # recursively permit
        loc = self.location
        while loc:
            loc.allowed_users.add(self.applicant)
            loc.save()
            loc = loc.parent

    def reject(self):
        self.rejected = True
        self.closed = True

    def __str__(self):
        return "{1} | {0}".format(self.applicant, self.location)

    class Meta:
        ordering = ['closed', 'id']
        verbose_name=_("位置申请")
        verbose_name_plural = verbose_name
