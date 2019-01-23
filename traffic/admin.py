from django.contrib import admin
from traffic.models import Traffic


class TrafficAdmin(admin.ModelAdmin):
    list_display = ('response_time', 'user', 'datetime', 'url', 'ip')


admin.site.register(Traffic, TrafficAdmin)
