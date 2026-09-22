from django.contrib import admin
from .models import TrainStatus

@admin.register(TrainStatus)
class TrainStatusAdmin(admin.ModelAdmin):
    list_display = ('train', 'date', 'status_message')
    search_fields = ('train__number', 'train__name')
    list_filter = ('status_message', 'date')
    list_per_page = 100
