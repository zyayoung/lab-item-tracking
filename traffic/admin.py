from django.contrib import admin
from traffic.models import Traffic


class TrafficAdmin(admin.ModelAdmin):
    list_display = (
        'response_time',
        'user',
        'datetime',
        'url',
        'ip',
        'http_status',
    )
    search_fields = ('user__name', 'url', 'ip')
    list_filter = ('http_status', 'user')
    date_hierarchy = 'datetime'


admin.site.register(Traffic, TrafficAdmin)
