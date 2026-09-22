import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from django.apps import apps
from django.core.management import call_command

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
Invoice = apps.get_model('bookings.Invoice')

print("--- POST-IMPORT COUNTS ---")
print(f"Stations: {Station.objects.count()}")
print(f"Trains: {Train.objects.count()}")
print(f"Routes: {Route.objects.count()}")
print(f"RouteStations: {RouteStation.objects.count()}")
print(f"Schedules: {Schedule.objects.count()}")
print(f"Users: {User.objects.count()}")
print(f"Bookings: {Booking.objects.count()}")
print(f"Passengers: {Passenger.objects.count()}")
print(f"PNRs: {PNR.objects.count()}")
print(f"Tickets: {Ticket.objects.count()}")

print("\n--- VALIDATING 12951 ---")
try:
    rajdhani = Train.objects.get(number='12951')
    print(f"Train 12951 Found: {rajdhani.name}")
    route = rajdhani.route
    print(f"Route Name: {route.name}")
    
    stations = route.stations.all().order_by('sequence_number')
    print(f"Total intermediate stops: {stations.count()}")
    for rs in stations[:5]:
        print(f" - {rs.sequence_number}: {rs.station.name} (Arr: {rs.arrival_time}, Dep: {rs.departure_time})")
    print(" ...")
    for rs in stations[stations.count()-3:]:
        print(f" - {rs.sequence_number}: {rs.station.name} (Arr: {rs.arrival_time}, Dep: {rs.departure_time})")
        
    has_coords = all(rs.station.latitude is not None and rs.station.longitude is not None for rs in stations)
    print(f"Coordinates present for all stations in route: {has_coords}")
except Train.DoesNotExist:
    print("Train 12951 NOT FOUND!")

print("\n--- RUNNING DJANGO CHECK ---")
call_command('check')
