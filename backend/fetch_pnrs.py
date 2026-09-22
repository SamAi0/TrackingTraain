import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from pnr.models import PNR

pnrs = PNR.objects.select_related('booking').all()[:10]

print("Valid PNRs:")
for p in pnrs:
    print(f"| {p.pnr_number} | {p.booking.train_number} | {p.booking.source_station} | {p.booking.destination_station} | {p.booking.journey_date} | {p.status} |")
