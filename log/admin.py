from django.contrib import admin
from .models import *

# Register your models here.


class LogAdmin(admin.ModelAdmin):
    list_display = ('operator', '_id', 'category', '_from', '_to', 'time')


admin.site.register(Log, LogAdmin)