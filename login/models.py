from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext as _


class User(models.Model):
    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    c_time = models.DateTimeField(auto_now_add=True)
    settings = JSONField(verbose_name='设置', blank=True, default=dict)
    staff = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        verbose_name="被管理员工",
        related_name="user_manager",
    )
    is_superadmin = models.BooleanField(
        default=False,
        verbose_name='超级管理员',
    )
    has_confirmed = models.BooleanField(default=False)

    def permission_str(self):
        if self.is_superadmin:
            return "超级管理员"
        elif self.staff.exists():
            return "主管"
        else:
            return "员工"

    def __str__(self):
        return "{0}{1}".format(self.name,
                                " (Admin)" if self.is_superadmin else "")

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + ":   " + self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"


class AllowedEmails(models.Model):
    email = models.EmailField(unique=True)
    real_name = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "邮箱白名单"
        verbose_name_plural = "邮箱白名单"
