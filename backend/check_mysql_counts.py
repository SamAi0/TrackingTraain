import os
import sys
import django

# Setup Django with MySQL settings
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
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

print("--- MySQL Table Row Counts ---")
total_rows = 0
for model_name in models_to_check:
    try:
        model = apps.get_model(model_name)
        count = model.objects.count()
        total_rows += count
        print(f"{model_name.split('.')[1].ljust(20)}: {count}")
    except Exception as e:
        print(f"{model_name.split('.')[1].ljust(20)}: ERROR - {str(e)}")

print(f"\nTotal TrackEase Records: {total_rows}")
