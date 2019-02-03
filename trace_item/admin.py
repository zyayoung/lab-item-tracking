from django.contrib import admin
from .models import *


class ItemLogAdmin(admin.ModelAdmin):
    list_display = ('item', 'operator', 'time')
    search_fields = ('item__name', 'operator__name')
    list_filter = ('operator',)
    date_hierarchy = 'time'


admin.site.register(ItemLog, ItemLogAdmin)
