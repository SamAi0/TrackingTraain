import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from stations.models import Station
from trains.models import Train
from routes.models import RouteStation

result = {}
result['station_count'] = Station.objects.count()
result['train_count'] = Train.objects.count()
result['train_12951_exists'] = Train.objects.filter(number='12951').exists()
result['train_01101_exists'] = Train.objects.filter(number='01101').exists()

if result['train_12951_exists']:
    result['train_12951_route_count'] = RouteStation.objects.filter(route__train__number='12951').count()
    
if result['train_01101_exists']:
    result['train_01101_route_count'] = RouteStation.objects.filter(route__train__number='01101').count()

print(json.dumps(result, indent=2))
