from django.contrib import admin
from .models import *


class ItemLogAdmin(admin.ModelAdmin):
    list_display = ('time', 'operator', 'operation')


admin.site.register(ItemLog, ItemLogAdmin)
