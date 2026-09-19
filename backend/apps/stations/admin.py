from django.contrib import admin
from .models import Station

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'state')
    search_fields = ('code', 'name', 'city', 'state')
    list_filter = ('state', 'city')
