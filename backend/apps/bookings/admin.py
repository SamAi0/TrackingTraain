from django.contrib import admin
from .models import Booking, Passenger, Invoice, FareRule, SystemNotification

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'train', 'source', 'destination', 'date_of_journey', 'status')
    search_fields = ('id', 'user__username', 'train__number', 'payment_id')
    list_filter = ('status', 'date_of_journey')
    list_per_page = 100

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'booking')
    search_fields = ('name', 'booking__id')
    list_per_page = 100

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'booking', 'total_amount', 'payment_status')
    search_fields = ('invoice_number', 'booking__id')
    list_per_page = 100

@admin.register(FareRule)
class FareRuleAdmin(admin.ModelAdmin):
    list_display = ('train_type', 'ticket_class', 'base_fare', 'per_km_rate', 'is_active')
    list_filter = ('train_type', 'is_active')
    list_per_page = 100

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'created_at', 'is_read')
    search_fields = ('user__username', 'message')
    list_filter = ('notification_type', 'is_read')
    list_per_page = 100
