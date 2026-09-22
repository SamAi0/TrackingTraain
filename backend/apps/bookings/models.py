from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

User = get_user_model()

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
        ('EXPIRED', 'Expired'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    train = models.ForeignKey('trains.Train', on_delete=models.SET_NULL, null=True)
    source = models.ForeignKey('stations.Station', on_delete=models.SET_NULL, related_name='booking_source', null=True)
    destination = models.ForeignKey('stations.Station', on_delete=models.SET_NULL, related_name='booking_destination', null=True)
    date_of_journey = models.DateField(null=True)
    ticket_class = models.CharField(max_length=10, blank=True, null=True)
    
    booking_date = models.DateTimeField(auto_now_add=True)
    
    base_fare = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    fee_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_fare = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Booking {self.id} for {self.user.username} - {self.status}"

class FareRule(models.Model):
    train_type = models.CharField(max_length=20, choices=[('EXPRESS', 'Express'), ('LOCAL', 'Local'), ('PASSENGER', 'Passenger'), ('SUPERFAST', 'Superfast')])
    ticket_class = models.CharField(max_length=10, blank=True, null=True, help_text="Applicable class (e.g., SL, 3A, GN). Leave blank for default local fare.")
    base_fare = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    per_km_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Fare Rule: {self.train_type} - {self.ticket_class or 'Default'}"

class Passenger(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, blank=True)
    berth_preference = models.CharField(max_length=20, blank=True)
    seat_number = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.name} ({self.age})"

def generate_invoice_number():
    return f"TE-INV-{get_random_string(8, allowed_chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"

class Invoice(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True, default=generate_invoice_number)
    invoice_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='PAID')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.invoice_number
class SystemNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('BOOKING_CONFIRM', 'Booking Confirmation'),
        ('BOOKING_CANCEL', 'Booking Cancellation'),
        ('TRAIN_STATUS', 'Train Status'),
        ('SYSTEM', 'System Alert'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='SYSTEM')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('INITIATED', 'Initiated'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
        ('EXPIRED', 'Expired'),
    )

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=50) # upi, card, netbanking, wallet
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='INITIATED')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    idempotency_key = models.CharField(max_length=100, blank=True, null=True)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    masked_details = models.JSONField(blank=True, null=True)
    
    success_for_booking = models.IntegerField(blank=True, null=True, unique=True, help_text="Set to booking_id if SUCCESS, else NULL for MySQL uniqueness")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id} - {self.status}"
