from django.contrib import admin
from .models import Route, RouteStation

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'train')
    search_fields = ('train__number', 'train__name')
    list_filter = ('train__train_type',)
    list_per_page = 100

@admin.register(RouteStation)
class RouteStationAdmin(admin.ModelAdmin):
    list_display = ('route', 'station', 'sequence_number', 'arrival_time', 'departure_time')
    search_fields = ('route__train__number', 'station__code', 'station__name')
    ordering = ('route', 'sequence_number')
    list_per_page = 100
