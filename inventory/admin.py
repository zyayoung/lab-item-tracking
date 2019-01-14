from django.contrib import admin
from inventory.models import Material

# class MaterialAdmin(admin.ModelAdmin):
#     # fields = ('name', 'location', 'quantity', 'unit')
#     list_display = ('name', 'location', 'quantity', 'unit')

# admin.site.register(Material, MaterialAdmin)

admin.site.register(Material)
