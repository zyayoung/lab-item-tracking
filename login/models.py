from django.db import models

# Create your models here.


class User(models.Model):

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    c_time = models.DateTimeField(auto_now_add=True)
    staff = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="关联用户",
        related_name="staffUser",
    )
    is_admin = models.BooleanField(
        verbose_name="是否管理员",
        default=False,
    )

    def __str__(self):
        return "{0}{1}".format(self.name, "(管理员)" if self.is_admin else "")

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "用户"
        verbose_name_plural = verbose_name
