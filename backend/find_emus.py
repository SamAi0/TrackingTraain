import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from trains.models import Train

print("Finding EMU / MEMU / SUBURBAN / LOCAL trains in the DB:")

types = Train.objects.values_list('train_type', flat=True).distinct()
print(f"All Train Types: {list(types)}")

# Let's see if there are any trains that have 'LOCAL' in type or name that have Mumbai stations
# We already found SDAH, HWH, MAS, HYB local trains earlier.
# Are there ANY Mumbai local trains? Let's check CCG, CSTM, KYN, BVI, PNVL, VR (Virar)
mumbai_station_codes = ['CSTM', 'KYN', 'BVI', 'PNVL', 'VR', 'DDR', 'DR', 'BA', 'BDTS']

trains = Train.objects.filter(
    route__stations__station__code__in=mumbai_station_codes,
    train_type__in=['EMU', 'MEMU', 'SUBURBAN', 'LOCAL']
).distinct()

for t in trains:
    stations = t.route.stations.select_related('station').order_by('sequence_number')
    if stations.exists():
        src = stations.first()
        dst = stations.last()
        print(f"Train: {t.number} | {t.name} | Type: {t.train_type} | Src: {src.station.name} ({src.station.code}) | Dst: {dst.station.name} ({dst.station.code})")

# If none found by type, check by name
if not trains.exists():
    print("No EMUs found by train_type. Checking by name containing LOCAL/EMU/FAST/SLOW...")
    trains_by_name = Train.objects.filter(
        route__stations__station__code__in=mumbai_station_codes,
    ).filter(name__icontains='LOCAL').distinct()
    
    for t in trains_by_name:
        stations = t.route.stations.select_related('station').order_by('sequence_number')
        src = stations.first()
        dst = stations.last()
        print(f"Train: {t.number} | {t.name} | Type: {t.train_type} | Src: {src.station.name} ({src.station.code}) | Dst: {dst.station.name} ({dst.station.code})")

