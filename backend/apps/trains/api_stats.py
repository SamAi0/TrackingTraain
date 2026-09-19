from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from stations.models import Station
from trains.models import Train
from routes.models import RouteStation
from django.db.models import Count, F, ExpressionWrapper, fields, Avg

class DashboardStatsAPIView(APIView):
    def get(self, request):
        cache_key = 'dashboard_stats'
        stats = cache.get(cache_key)
        
        if not stats:
            # 1. Zone-wise stations
            zone_stations = list(Station.objects.exclude(zone__isnull=True).exclude(zone='').values('zone').annotate(count=Count('code')).order_by('-count'))
            
            # 2. State-wise stations
            state_stations = list(Station.objects.exclude(state__isnull=True).exclude(state='').values('state').annotate(count=Count('code')).order_by('-count'))
            
            # 3. Running day distribution
            trains = list(Train.objects.all().values('running_days'))
            days_count = {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0, 'SUN': 0}
            for t in trains:
                rd = t['running_days'] or {}
                for day, runs in rd.items():
                    if runs and day in days_count:
                        days_count[day] += 1
            
            # 4. Busiest stations by train count
            busiest_stations = list(
                RouteStation.objects.values('station__name', 'station__code', 'station__zone')
                .annotate(train_count=Count('route', distinct=True))
                .order_by('-train_count')[:10]
            )
            
            # 5. Average halt time
            halt_sample = RouteStation.objects.exclude(arrival_time__isnull=True).exclude(departure_time__isnull=True).values('arrival_time', 'departure_time')[:5000]
            total_seconds = 0
            count = 0
            for h in halt_sample:
                arr = h['arrival_time']
                dep = h['departure_time']
                if arr and dep:
                    arr_sec = arr.hour * 3600 + arr.minute * 60 + arr.second
                    dep_sec = dep.hour * 3600 + dep.minute * 60 + dep.second
                    diff = dep_sec - arr_sec
                    if diff < 0:
                        diff += 86400 # Next day
                    if diff > 0 and diff < 3600: # Exclude anomalies > 1 hr
                        total_seconds += diff
                        count += 1
            avg_halt = (total_seconds / count / 60.0) if count > 0 else 2.5
            
            # Zone-wise trains (by source station zone)
            zone_trains = list(Train.objects.exclude(source__zone__isnull=True).exclude(source__zone='').values(zone=F('source__zone')).annotate(count=Count('number')).order_by('-count'))
            
            stats = {
                'zone_stations': zone_stations,
                'state_stations': state_stations,
                'running_days': days_count,
                'busiest_stations': busiest_stations,
                'average_halt_minutes': round(avg_halt, 1),
                'zone_trains': zone_trains,
                'total_stations': Station.objects.count(),
                'total_trains': Train.objects.count()
            }
            cache.set(cache_key, stats, timeout=86400) # 24 hour cache
            
        return Response(stats)
