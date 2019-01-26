from django.contrib import admin

# Register your models here.

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'c_time', 'is_superadmin', 'permission_str')


admin.site.register(User, UserAdmin)
