from django.contrib import admin
from .models import Train

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'train_type')
    search_fields = ('number', 'name')
    list_filter = ('train_type',)
    list_per_page = 100
