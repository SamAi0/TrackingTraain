import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from trains.models import Train
from django.db.models import Count

# We know from history there are 6 Mumbai suburban trains imported.
# Let's find trains with type 'LOCAL' or 'SUBURBAN', or just query trains that were recently added or have specific known numbers if possible, 
# but let's query all trains with 'LOCAL' or 'FAST' or 'SLOW' in type or name, or that have 'LOCAL' in train_type.
# Also, they might just have type 'LOCAL'

trains = Train.objects.filter(train_type__icontains='LOCAL') | Train.objects.filter(name__icontains='LOCAL')

# If they don't have 'LOCAL' in type, let's just query everything and filter by name or known Mumbai stations.
# Let's see what we get first.

if not trains.exists():
    # Maybe they are 'SUBURBAN'
    trains = Train.objects.filter(train_type__icontains='SUBURBAN') | Train.objects.filter(name__icontains='FAST') | Train.objects.filter(name__icontains='SLOW')

# Mumbai Local Train Station Codes
mumbai_codes = ['CCG', 'VR', 'BVI', 'CSMT', 'CSST', 'CSTM', 'KYN', 'PNVL', 'TNA', 'KJT', 'KSRA', 'BSR', 'VDLR']

# Find trains where source AND destination are in mumbai_codes, or just one is and they are short distance
trains = Train.objects.filter(
    route__stations__station__code__in=mumbai_codes
).distinct()

mumbai_trains = []
for t in trains:
    stations = t.route.stations.select_related('station').order_by('sequence_number')
    if stations.exists():
        src = stations.first()
        dst = stations.last()
        
        # A Mumbai local usually operates entirely within Mumbai and has many stops.
        # Let's filter to trains with distance < 200km or stops > 10, and running between Mumbai stations.
        if src.station.code in mumbai_codes or dst.station.code in mumbai_codes:
            if 'LOCAL' in t.train_type.upper() or 'LOCAL' in t.name.upper() or 'EMU' in t.name.upper() or 'MEMU' in t.name.upper():
                mumbai_trains.append((t, src, dst, stations.count()))
            elif stations.count() > 10 and (src.station.code in mumbai_codes and dst.station.code in mumbai_codes):
                mumbai_trains.append((t, src, dst, stations.count()))

for t, src, dst, count in mumbai_trains:
    print(f"Train: {t.number} | {t.name} | Type: {t.train_type} | Src: {src.station.name} ({src.station.code}) | Dst: {dst.station.name} ({dst.station.code}) | Stops: {count}")

