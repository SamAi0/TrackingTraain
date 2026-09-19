from django.contrib import admin
from .models import Booking, Passenger, Invoice, FareRule, SystemNotification

class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'train', 'source', 'destination', 'date_of_journey', 'ticket_class', 'status', 'total_fare']
    list_filter = ['status', 'date_of_journey', 'train__train_type']
    search_fields = ['id', 'user__username', 'train__number']
    inlines = [PassengerInline]

@admin.register(FareRule)
class FareRuleAdmin(admin.ModelAdmin):
    list_display = ['train_type', 'ticket_class', 'base_fare', 'per_km_rate', 'is_active']
    list_filter = ['train_type', 'is_active', 'ticket_class']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'booking', 'total_amount', 'payment_status', 'transaction_id']
    search_fields = ['invoice_number', 'transaction_id', 'booking__id']
    list_filter = ['payment_status']

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'message', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
