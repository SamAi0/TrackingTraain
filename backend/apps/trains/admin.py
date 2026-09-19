from django.contrib import admin
from .models import Train

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'train_type', 'source', 'destination')
    search_fields = ('number', 'name')
    list_filter = ('train_type',)
