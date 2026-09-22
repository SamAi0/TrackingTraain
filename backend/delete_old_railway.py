import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from django.apps import apps
from django.db import transaction

Station = apps.get_model('stations.Station')
Train = apps.get_model('trains.Train')
Route = apps.get_model('routes.Route')
RouteStation = apps.get_model('routes.RouteStation')
Schedule = apps.get_model('schedules.Schedule')

# App data models
User = apps.get_model('accounts.User')
Booking = apps.get_model('bookings.Booking')
Passenger = apps.get_model('bookings.Passenger')
PNR = apps.get_model('pnr.PNR')
Ticket = apps.get_model('pnr.Ticket')

def get_counts():
    return {
        'stations': Station.objects.count(),
        'trains': Train.objects.count(),
        'routes': Route.objects.count(),
        'routestations': RouteStation.objects.count(),
        'schedules': Schedule.objects.count(),
        'users': User.objects.count(),
        'bookings': Booking.objects.count(),
        'passengers': Passenger.objects.count(),
        'pnrs': PNR.objects.count(),
        'tickets': Ticket.objects.count(),
    }

print("=== BEFORE DELETION ===")
counts = get_counts()
for k, v in counts.items():
    print(f"{k}: {v}")

print("\nExecuting Deletion...")
with transaction.atomic():
    # Order matters for FK constraints:
    Schedule.objects.all().delete()
    RouteStation.objects.all().delete()
    Route.objects.all().delete()
    Train.objects.all().delete()
    Station.objects.all().delete()

print("\n=== AFTER DELETION ===")
counts_after = get_counts()
for k, v in counts_after.items():
    print(f"{k}: {v}")
