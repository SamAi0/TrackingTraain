from django.contrib import admin
from .models import Station

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'state', 'latitude', 'longitude')
    search_fields = ('code', 'name')
    list_filter = ('state', 'zone')
    list_per_page = 100
