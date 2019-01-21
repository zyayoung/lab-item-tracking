from django.contrib import admin
from .models import *


class ItemLogAdmin(admin.ModelAdmin):
    list_display = ('item', 'operation', 'operator', 'time')

admin.site.register(ItemLog, ItemLogAdmin)
