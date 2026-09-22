import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from trains.models import Train
from django.db.models import Count

import datetime

# Find 10 trains that have valid routes and a good number of stations (> 10)
trains = Train.objects.annotate(
    station_count=Count('route__stations')
).filter(
    station_count__gt=10
).exclude(
    number='12951'  # Let's exclude the one we already tested heavily
)[:10]

for t in trains:
    stations = t.route.stations.select_related('station').order_by('sequence_number')
    if stations.exists():
        src = stations.first()
        dst = stations.last()
        print(f"| {t.number} | {t.name} | {src.station.name} ({src.station.code}) | {dst.station.name} ({dst.station.code}) | {src.departure_time.strftime('%H:%M') if src.departure_time else '--:--'} | {dst.arrival_time.strftime('%H:%M') if dst.arrival_time else '--:--'} | {t.station_count} | {datetime.date.today().strftime('%Y-%m-%d')} |")

