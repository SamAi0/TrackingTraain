from django.contrib import admin
from .models import RapidAPIHistory

@admin.register(RapidAPIHistory)
class RapidAPIHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'endpoint', 'train_number', 'http_status', 'success', 'timestamp')
    list_filter = ('success', 'http_status', 'endpoint')
    search_fields = ('endpoint', 'train_number')
    readonly_fields = ('timestamp', 'endpoint', 'train_number', 'request_params', 'http_status', 'success', 'response_json')
