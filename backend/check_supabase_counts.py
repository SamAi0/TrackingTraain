import os
import sys
import django

sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps

models_to_check = [
    'stations.Station',
    'trains.Train',
    'routes.Route',
    'routes.RouteStation',
    'schedules.Schedule',
    'accounts.User',
    'bookings.Booking',
    'pnr.PNR',
    'pnr.Ticket',
    'bookings.Invoice',
    'bookings.FareRule',
    'bookings.Payment',
    'bookings.SystemNotification'
]

print("--- Current Supabase Counts ---")
total = 0
for model_name in models_to_check:
    count = apps.get_model(model_name).objects.count()
    total += count
    print(f"{model_name.split('.')[1].ljust(20)}: {count}")
print(f"Total TrackEase Records: {total}")
