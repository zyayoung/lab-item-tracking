from django.db import models
from login.models import User


class Traffic(models.Model):
    url = models.CharField(max_length=64, verbose_name="URL")
    response_time = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name="Response Time",
    )
    datetime = models.DateTimeField(auto_now_add=True, verbose_name="Request Time")
    ip = models.CharField(max_length=16, verbose_name="IP")
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="User",
        related_name="user",
    )
    http_status = models.CharField(max_length=16, verbose_name="HTTP Status")
