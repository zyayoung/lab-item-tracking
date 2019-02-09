from django.contrib import admin
from .models import *

# Register your models here.


class LogAdmin(admin.ModelAdmin):
    list_display = (
        'operator',
        'obj_id',
        'category',
        'attribute',
        'before',
        'after',
        'time',
    )


admin.site.register(Log, LogAdmin)