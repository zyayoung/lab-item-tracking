from django.contrib import admin
from .models import *


class LocationPermissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('location', 'applicant', 'time', 'auditor')


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'unit', 'location', 'owner', 'is_public', 'update_time')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'path', 'is_public', 'allowed_users_summary')


admin.site.register(Item, ItemAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(LocationPermissionApplication, LocationPermissionApplicationAdmin)
