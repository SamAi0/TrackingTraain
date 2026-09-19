from django.contrib import admin
from .models import Route, RouteStation
from schedules.models import Schedule

class RouteStationInline(admin.TabularInline):
    model = RouteStation
    extra = 0
    ordering = ('sequence_number',)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'train')
    search_fields = ('train__number', 'train__name')
    inlines = [RouteStationInline]

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('train', 'station', 'arrival_time', 'departure_time', 'day_count')
    search_fields = ('train__number', 'station__code', 'station__name')
    list_filter = ('day_count',)
