from django.contrib import admin
from .models import PNR, Ticket

@admin.register(PNR)
class PNRAdmin(admin.ModelAdmin):
    list_display = ('pnr_number', 'booking', 'status', 'created_at')
    search_fields = ('pnr_number', 'booking__id')
    list_filter = ('status', 'created_at')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'booking', 'ticket_class', 'generated_at')
    search_fields = ('ticket_number', 'booking__id', 'booking__pnr_record__pnr_number')
    list_filter = ('ticket_class', 'generated_at')
