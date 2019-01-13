# -*- coding: utf-8 -*-
# -*- mode: python -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from login.models import User as myUser
import datetime


class Category(models.Model):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']


class Unit(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Manufacturer(models.Model):
    name = models.CharField(max_length=64)
    url = models.CharField(max_length=64, blank=True, null=True)
    lookup_url = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="url pattern to look up part number")
    rep = models.CharField(max_length=128, blank=True, null=True)
    rep_phone = models.CharField(max_length=16, blank=True, null=True)
    rep_email = models.CharField(max_length=64, blank=True, null=True)
    support_phone = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Vendor(models.Model):
    name = models.CharField(max_length=64)
    url = models.CharField(max_length=64, blank=True, null=True)
    lookup_url = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="url pattern to look up catalog number")
    phone = models.CharField(max_length=16, blank=True, null=True)
    rep = models.CharField(max_length=45, blank=True, null=True)
    rep_phone = models.CharField(max_length=16, blank=True, null=True)
    rep_email = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Client(models.Model):
    company = models.CharField(max_length=64, blank=True, verbose_name="委托单位")
    name = models.CharField(max_length=64, verbose_name="委托人")
    address = models.CharField(max_length=128, blank=True, verbose_name="委托人联系地址")
    phone = models.CharField(max_length=16, blank=True, null=True, verbose_name="委托人手机号")
    email = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托人邮箱")
    othercontacts = models.CharField(max_length=64, blank=True, null=True, verbose_name="委托人其他联系方式")

    def __str__(self):
        return self.company + ' ' + self.name

    class Meta:
        ordering = ['name']
        verbose_name = "委托人"
        verbose_name_plural = verbose_name


class PTAO(models.Model):
    code = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=128)
    expires = models.DateField(blank=True, null=True)

    def active(self):
        if self.expires:
            return datetime.date.today() < self.expires
        else:
            return True

    def __str__(self):
        return "%s (%s)" % (self.code, self.description)

    class Meta:
        ordering = ['code']
        verbose_name = "PTAO"
        verbose_name_plural = "PTAOs"


class Item(models.Model):
    name = models.CharField(max_length=128)
    chem_formula = models.CharField(
        'Chemical formula', max_length=45, blank=True, null=True)

    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    catalog = models.CharField(
        'Catalog number', max_length=45, blank=True, null=True)
    manufacturer = models.ForeignKey(
        'Manufacturer',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="leave blank if unknown or same as vendor")
    manufacturer_number = models.CharField(
        max_length=45, blank=True, null=True)
    size = models.DecimalField(
        'Size of unit', max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    date_added = models.DateField(auto_now_add=True)
    parent_item = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="example: for printer cartriges, select printer")
    comments = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def unit_size(self):
        return "%s%s%s" % (self.size or "", "" if str(
            self.unit).startswith("/") else " ", self.unit)

    def total_price(self):
        return (self.cost or 0) * self.units_purchased

    def vendor_url(self):
        try:
            return self.vendor.lookup_url % self.catalog
        except (AttributeError, TypeError):
            return None

    def mfg_url(self):
        try:
            return self.manufacturer.lookup_url % self.manufacturer_number
        except (AttributeError, TypeError):
            return None

    def get_absolute_url(self):
        return reverse("inventory:item", kwargs={'pk': self.pk})


class Order(models.Model):
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(Item, through='OrderItem')
    ptao = models.ForeignKey(
        PTAO, blank=True, null=True, on_delete=models.SET_NULL)
    ordered = models.BooleanField()
    order_date = models.DateField(default=datetime.date.today)
    ordered_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        if self.ordered:
            status = self.order_date
        else:
            status = "in progress"
        return "%s (%s)" % (self.name, status)

    @property
    def item_count(self):
        return self.items.count

    def get_absolute_url(self):
        return reverse("inventory:order", kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-order_date', 'name']


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    units_purchased = models.IntegerField()
    cost = models.DecimalField(
        'Cost per unit',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True)

    date_arrived = models.DateField(blank=True, null=True)
    serial = models.CharField(
        'Serial number', max_length=45, blank=True, null=True)
    uva_equip = models.CharField(
        'UVa equipment number', max_length=32, blank=True, null=True)
    location = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        help_text="example: -80 freezer, refrigerator, Gilmer 283")
    expiry_years = models.DecimalField(
        'Warranty or Item expiration (y)',
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True)

    reconciled = models.BooleanField()

    def total_price(self):
        return (self.cost or 0) * self.units_purchased

    def name(self):
        return self.item.name

    def order_date(self):
        return self.order.order_date

    def __str__(self):
        return "%s [%s]" % (self.item.name, self.order.order_date)

    class Meta:
        db_table = "inventory_order_items"


class Location(models.Model):
    loc1 = models.CharField(
        max_length=45, verbose_name="位置1", blank=True, null=True)
    loc2 = models.CharField(
        max_length=45, verbose_name="位置2", blank=True, null=True)
    loc3 = models.CharField(
        max_length=45, verbose_name="位置3", blank=True, null=True)
    loc4 = models.CharField(
        max_length=45, verbose_name="位置4", blank=True, null=True)
    loc5 = models.CharField(
        max_length=45, verbose_name="位置5", blank=True, null=True)

    def __str__(self):
        re = self.loc1 if self.loc1 else ""
        re += self.loc2 + " " if self.loc2 else ""
        re += self.loc3 + " " if self.loc3 else ""
        re += self.loc4 + " " if self.loc4 else ""
        re += self.loc5 if self.loc5 else ""
        return re

    class Meta:
        ordering = ['loc1']


class Material(models.Model):
    name = models.CharField(max_length=128, verbose_name="名称")
    location = models.ForeignKey(
        Location, verbose_name="位置", on_delete=models.PROTECT)
    quantity = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        blank=True,
        verbose_name="数量")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="单位")
    attribute = models.TextField(blank=True, verbose_name="属性")
    user = models.ManyToManyField(myUser, default='', verbose_name="用户")

    class Meta:
        ordering = ['id']
        verbose_name = "物品"
        verbose_name_plural = verbose_name
