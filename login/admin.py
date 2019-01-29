from django.contrib import admin

# Register your models here.

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'c_time', 'permission_str')
    search_fields = ('name', 'email')
    list_filter = ('is_superadmin',)
    filter_horizontal = ('staff',)


admin.site.register(User, UserAdmin)
admin.site.register(ConfirmString)
