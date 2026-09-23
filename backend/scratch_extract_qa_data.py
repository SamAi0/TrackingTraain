import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from stations.models import Station
from trains.models import Train
from routes.models import RouteStation

data = {}

stations = list(Station.objects.all().values('name', 'code', 'city', 'state', 'zone', 'latitude', 'longitude')[:50])
data['stations'] = stations

trains = Train.objects.all()
t_list = []
for t in trains:
    t_list.append({
        'number': t.number,
        'name': t.name,
        'source': t.source.code if t.source else None,
        'destination': t.destination.code if t.destination else None
    })
data['trains'] = t_list

pairs = []
for t in trains:
    rs = list(RouteStation.objects.filter(route__train=t).order_by('sequence_number'))
    if len(rs) > 1:
        pairs.append({
            'train': t.number,
            'source': rs[0].station.code,
            'destination': rs[-1].station.code,
        })
data['route_pairs'] = pairs

try:
    from pnr.models import PNR
    pnrs = list(PNR.objects.all().values('pnr_number', 'booking__train__number', 'status')[:10])
    data['pnrs'] = pnrs
except Exception:
    data['pnrs'] = []

print(json.dumps(data))
