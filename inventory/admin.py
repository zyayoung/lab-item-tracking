from django.contrib import admin
from .models import *


class LocationPermissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('location', 'applicant', 'time', 'auditor')


admin.site.register(Item)
admin.site.register(Location)
admin.site.register(LocationPermissionApplication, LocationPermissionApplicationAdmin)
