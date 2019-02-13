from django.contrib import admin

# Register your models here.

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'c_time',
        'permission_str',
        'latest_online_time',
    )
    search_fields = ('name', 'email')
    list_filter = ('is_superadmin', )
    filter_horizontal = ('staff', )


class AllowedEmailsAdmin(admin.ModelAdmin):
    list_display = ('email', 'real_name')
    search_fields = ('real_name', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(AllowedEmails, AllowedEmailsAdmin)
admin.site.register(ConfirmString)
