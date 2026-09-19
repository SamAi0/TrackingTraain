from django.db import models
from django.utils.crypto import get_random_string

def generate_pnr():
    return get_random_string(10, allowed_chars='0123456789')

class PNR(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Confirmed'),
        ('WAITLISTED', 'Waitlisted'),
        ('CANCELLED', 'Cancelled'),
    )
    pnr_number = models.CharField(max_length=10, primary_key=True, default=generate_pnr)
    # The booking is the source of truth for passengers, train, source, destination, date.
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='pnr_record', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PNR: {self.pnr_number} - {self.status}"

class Ticket(models.Model):
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='ticket')
    ticket_number = models.CharField(max_length=20, unique=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    ticket_class = models.CharField(max_length=10, default='SL')

    def __str__(self):
        return self.ticket_number
