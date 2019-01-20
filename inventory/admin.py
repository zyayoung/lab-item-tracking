from django.contrib import admin
from inventory.models import *


admin.site.register(Item)
admin.site.register(ItemLog)
admin.site.register(Location)
admin.site.register(LocationPermissionApplication)
