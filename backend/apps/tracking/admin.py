from django.contrib import admin
from .models import TrainStatus

@admin.register(TrainStatus)
class TrainStatusAdmin(admin.ModelAdmin):
    list_display = ('train', 'date', 'current_station', 'status_message', 'is_simulated')
    search_fields = ('train__number', 'train__name', 'current_station__code')
    list_filter = ('status_message', 'date')

    def is_simulated(self, obj):
        return "DEMO • SIMULATED LIVE DATA"
    is_simulated.short_description = "Data Source"
