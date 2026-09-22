from django.contrib import admin
from .models import Schedule

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('train', 'station', 'day_count', 'arrival_time', 'departure_time')
    search_fields = ('train__number', 'train__name', 'station__code', 'station__name')
    list_filter = ('train__train_type',)
    ordering = ('train', 'day_count', 'arrival_time')
    list_per_page = 100
