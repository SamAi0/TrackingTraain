from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Station

class StationAutocompleteAPIView(APIView):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        
        data = []
        popular_trains = []
        target_station = None
        if not q:
            popular_codes = ['NDLS', 'BCT', 'CSMT', 'HWH', 'MAS', 'SBC', 'PUNE', 'ST']
            stations = Station.objects.filter(code__in=popular_codes).order_by('name')
            for st in stations:
                data.append({
                    'code': st.code,
                    'name': st.name,
                    'city': st.city,
                    'state': st.state,
                    'latitude': st.latitude,
                    'longitude': st.longitude
                })
            return Response({'success': True, 'data': data, 'popular_trains': []}, status=status.HTTP_200_OK)
        # Fast local DB search
        stations = Station.objects.filter(
            Q(code__icontains=q) | 
            Q(name__icontains=q)
        ).order_by('name')[:10]
        
        if stations.exists():
            first_st = stations.first()
            target_station = first_st.name
            from trains.models import Train
            # Get popular trains passing through this station
            trains = Train.objects.filter(route__stations__station=first_st).distinct()[:5]
            for t in trains:
                popular_trains.append({
                    'number': t.number,
                    'name': t.name
                })
        
        for st in stations:
            data.append({
                'code': st.code,
                'name': st.name,
                'city': st.city,
                'state': st.state,
                'latitude': st.latitude,
                'longitude': st.longitude
            })
            
        return Response({
            'success': True, 
            'data': data, 
            'popular_trains': popular_trains, 
            'target_station': target_station
        }, status=status.HTTP_200_OK)

from django.core.paginator import Paginator

class StationListAPIView(APIView):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        zone = request.GET.get('zone', '').strip()
        state = request.GET.get('state', '').strip()
        page = request.GET.get('page', '1')
        
        stations = Station.objects.all().order_by('name')
        
        if q:
            stations = stations.filter(Q(code__icontains=q) | Q(name__icontains=q))
        if zone:
            stations = stations.filter(zone=zone)
        if state:
            stations = stations.filter(state=state)
            
        paginator = Paginator(stations, 20) # 20 per page
        try:
            p = paginator.page(page)
        except:
            p = paginator.page(1)
            
        data = []
        for st in p.object_list:
            data.append({
                'code': st.code,
                'name': st.name,
                'state': st.state,
                'zone': st.zone,
                'latitude': st.latitude,
                'longitude': st.longitude
            })
            
        return Response({
            'count': paginator.count,
            'next': p.has_next() if hasattr(p, 'has_next') else False,
            'previous': p.has_previous() if hasattr(p, 'has_previous') else False,
            'results': data
        })

class StationGeoAPIView(APIView):
    def get(self, request):
        stations = Station.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).values('code', 'name', 'latitude', 'longitude')
        # Limit to 1000 for performance on the map, or all if feasible. We'll return all.
        data = [{'code': s['code'], 'name': s['name'], 'lat': s['latitude'], 'lng': s['longitude']} for s in stations]
        return Response({'success': True, 'data': data})

