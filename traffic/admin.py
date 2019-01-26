from django.contrib import admin
from traffic.models import Traffic


class TrafficAdmin(admin.ModelAdmin):
    list_display = (
        'response_time',
        'user',
        'datetime',
        'url',
        'ip',
        'user_agent',
        'http_status',
    )


admin.site.register(Traffic, TrafficAdmin)
