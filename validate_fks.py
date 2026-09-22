import os
import sys
import django

sys.path.insert(0, os.path.abspath('backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_migration'
django.setup()

from trains.models import Train
from routes.models import Route, RouteStation
from schedules.models import Schedule
from bookings.models import Booking
from pnr.models import PNR
from accounts.models import User

print("--- Validating Foreign Keys on Supabase ---")
print(f"Total Trains: {Train.objects.count()}")
print(f"Routes with a Train: {Route.objects.filter(train__isnull=False).count()} / {Route.objects.count()}")
print(f"RouteStations with a Route: {RouteStation.objects.filter(route__isnull=False).count()} / {RouteStation.objects.count()}")
print(f"Schedules with a RouteStation: {Schedule.objects.filter(route_station__isnull=False).count()} / {Schedule.objects.count()}")

print(f"\nTotal Bookings: {Booking.objects.count()}")
print(f"Bookings with a User: {Booking.objects.filter(user__isnull=False).count()} / {Booking.objects.count()}")
print(f"PNRs with a Booking: {PNR.objects.filter(booking__isnull=False).count()} / {PNR.objects.count()}")
