import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from stations.models import Station
from trains.models import Train
from django.db import connection

print("Mumbai Stations:")
for s in Station.objects.filter(name__icontains='MUMBAI'):
    print(f"{s.code} - {s.name}")
    
for s in Station.objects.filter(name__icontains='BOMBAY'):
    print(f"{s.code} - {s.name}")

for s in Station.objects.filter(name__icontains='BANDRA'):
    print(f"{s.code} - {s.name}")

for s in Station.objects.filter(name__icontains='BORIVALI'):
    print(f"{s.code} - {s.name}")

for s in Station.objects.filter(name__icontains='KALYAN'):
    print(f"{s.code} - {s.name}")
    
for s in Station.objects.filter(name__icontains='PANVEL'):
    print(f"{s.code} - {s.name}")

print("\nTrains terminating in Mumbai:")
with connection.cursor() as cursor:
    cursor.execute('''
        SELECT t.number, t.name, t.train_type
        FROM trains_train t
        JOIN routes_route r ON r.train_id = t.number
        JOIN routes_routestation rs1 ON rs1.route_id = r.id
        JOIN routes_routestation rs2 ON rs2.route_id = r.id
        WHERE (rs1.station_id IN (SELECT code FROM stations_station WHERE name LIKE 'MUMBAI%' OR name LIKE 'BANDRA%' OR name LIKE 'KALYAN%'))
        AND (rs2.station_id IN (SELECT code FROM stations_station WHERE name LIKE 'MUMBAI%' OR name LIKE 'BANDRA%' OR name LIKE 'KALYAN%'))
        AND rs1.station_id != rs2.station_id
    ''')
    rows = cursor.fetchall()
    print(f"Count: {len(rows)}")
    for row in rows[:10]:
        print(row)
