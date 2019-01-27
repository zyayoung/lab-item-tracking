from django.db import models
from login.models import User


class Traffic(models.Model):
    url = models.CharField(
        max_length=128,
        verbose_name="URL",
    )
    response_time = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name="Response Time",
    )
    datetime = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Request Time",
    )
    ip = models.CharField(
        max_length=16,
        verbose_name="IP",
    )
    user_agent = models.CharField(
        max_length=256,
        null=True,
        default="unknown",
        verbose_name="User-Agent",
    )
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="User",
        related_name="user_traffic",
    )
    http_status = models.CharField(
        max_length=16,
        verbose_name="HTTP Status",
    )


class CalenderCache(models.Model):
    date_str = models.CharField(max_length=32)
    traffic_cnt = models.IntegerField()
    locreq_cnt = models.IntegerField()
    itemlog_cnt = models.IntegerField()
    need_update = models.BooleanField(blank=True, default=True)
