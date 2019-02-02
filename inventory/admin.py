from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group, User
from django.views.decorators.cache import never_cache


class LocationPermissionApplicationAdmin(admin.ModelAdmin):
    list_display = ('location', 'applicant', 'time', 'auditor')
    search_fields = ('location__path', 'applicant__name', 'auditor__name')
    list_filter = ('applicant', 'auditor', 'location')
    date_hierarchy = 'time'


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'template', 'owner', 'is_public')
    search_fields = ('name', 'owner__name', 'location__path')
    list_filter = ('is_public', 'owner')
    filter_horizontal = ('allowed_users',)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'path', 'is_public', 'allowed_users_summary')
    search_fields = ('path',)
    filter_horizontal = ('allowed_users',)


class ItemTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_property', 'extra_data')
    search_fields = ('name', 'extra_data')
    list_filter = ('is_property', )
    date_hierarchy = 'create_time'


admin.site.site_header = "实验室物品数据库"
admin.site.site_title = "数据库"

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(ItemTemplate, ItemTemplateAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(LocationPermissionApplication, LocationPermissionApplicationAdmin)
