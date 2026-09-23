import os
import sys
import django
import json

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from stations.models import Station

with open('data/mumbai_suburban/trans_harbour_line_2024_clean.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

names = set(st['station_name'] for s in data['services'] for st in s['stations'])

res = {}
for n in names:
    db_sts = list(Station.objects.filter(name__iexact=n))
    res[n] = [s.code for s in db_sts]

print(json.dumps(res, indent=2))
