from django.db import models

# Create your models here.


class User(models.Model):

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    c_time = models.DateTimeField(auto_now_add=True)
    staff = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        verbose_name="被管理员工",
        related_name="staffUser",
    )

    def __str__(self):
        return "{0} {1}".format(self.name, "(管理员)" if self.staff.exists() else "")

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "用户"
        verbose_name_plural = verbose_name
