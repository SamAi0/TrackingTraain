import os, sys, django
sys.path.append('c:/Users/Asus/Desktop/Personal/rgc lcg/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from trains.models import Train
from routes.models import RouteStation
from django.db.models import Count, Q

print("## A. Database Evidence")

# 1. Fake Services
exists_99999 = Train.objects.filter(number='99999').exists()
exists_99998 = Train.objects.filter(number='99998').exists()
print(f"Train 99999 exists: {exists_99999}")
print(f"Train 99998 exists: {exists_99998}")
rs_fake = RouteStation.objects.filter(route__train__number__in=['99999', '99998']).count()
print(f"RouteStations connected to 99999/99998: {rs_fake}")

# 2. Zero Distance
zero_dist_total = RouteStation.objects.filter(distance_from_source=0).count()
zero_dist_seq1 = RouteStation.objects.filter(distance_from_source=0, sequence_number=1).count()
zero_dist_seq_gt1 = RouteStation.objects.filter(distance_from_source=0, sequence_number__gt=1).count()
print(f"\nRouteStation.distance_from_source = 0")
print(f"Total count: {zero_dist_total}")
print(f"Belong to sequence 1: {zero_dist_seq1}")
print(f"Belong to sequence > 1: {zero_dist_seq_gt1}")

# 3. NULL Distance
null_dist_total = RouteStation.objects.filter(distance_from_source__isnull=True).count()
# Suburban vs Other data: Assuming Suburban data has train type 'LOCAL'
null_dist_suburban = RouteStation.objects.filter(distance_from_source__isnull=True, route__train__train_type='LOCAL').count()
null_dist_other = RouteStation.objects.filter(distance_from_source__isnull=True).exclude(route__train__train_type='LOCAL').count()
print(f"\nRouteStation.distance_from_source IS NULL")
print(f"Total count: {null_dist_total}")
print(f"Belong to suburban data (LOCAL): {null_dist_suburban}")
print(f"Belong to other railway data: {null_dist_other}")

# 4. Verify Timings
arr_null = RouteStation.objects.filter(arrival_time__isnull=True).count()
dep_null = RouteStation.objects.filter(departure_time__isnull=True).count()
both_null = RouteStation.objects.filter(arrival_time__isnull=True, departure_time__isnull=True).count()
print(f"\nTimings IS NULL:")
print(f"arrival_time IS NULL: {arr_null}")
print(f"departure_time IS NULL: {dep_null}")
print(f"both NULL: {both_null}")

# Print a specific train for completeness check
print("\n## E. Timetable Evidence")
sub_trains = Train.objects.filter(train_type='LOCAL')
for t in sub_trains[:3]:
    print(f"Train {t.number} - Completeness: {t.running_days.get('timetable_complete') if t.running_days else 'Unknown'} - Route stops count: {t.route.stations.count()}")
    stops = t.route.stations.all()
    for s in stops[:2]:
         print(f"  Seq {s.sequence_number}: {s.station.code} - Arr: {s.arrival_time}, Dep: {s.departure_time}")
