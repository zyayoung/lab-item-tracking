from django.contrib import admin
from .models import *


class ItemLogAdmin(admin.ModelAdmin):
    list_display = ('item', 'operation', 'operator', 'time')
    search_fields = ('item__name', 'operator__name', 'location_from__id', 'location_to__id')


admin.site.register(ItemLog, ItemLogAdmin)
