from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking

class Command(BaseCommand):
    help = 'Expires pending bookings whose expires_at time has passed'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_count = Booking.objects.filter(
            status='PENDING', 
            expires_at__lt=now
        ).update(status='EXPIRED')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully expired {expired_count} pending bookings.'))
