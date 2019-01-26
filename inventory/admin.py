from django.contrib import admin
from .models import *


class LocationPermissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('location', 'applicant', 'time', 'auditor')
    search_fields = ('location__path', 'applicant__name', 'auditor__name')
    list_filter = ('applicant', 'auditor', 'location')


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'unit', 'location', 'owner', 'is_public')
    search_fields = ('name', 'unit', 'owner__name', 'location__path')
    list_filter = ('is_public', 'owner', 'unit')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'path', 'is_public', 'allowed_users_summary')
    search_fields = ('path',)


admin.site.register(Item, ItemAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(LocationPermissionApplication, LocationPermissionApplicationAdmin)
