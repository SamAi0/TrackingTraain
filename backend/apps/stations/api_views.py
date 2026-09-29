from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Station

class StationAutocompleteAPIView(APIView):
    def get(self, request):
        from railway_api.services.station_service import StationService
        q = request.GET.get('q', '').strip()
        
        result = StationService.search_station(q)
        # Adding an empty popular_trains to prevent frontend errors if they assume it exists
        if result.get('success'):
            result['popular_trains'] = []
            
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)

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



class StationTrainsAPIView(APIView):
    def get(self, request, code):
        from routes.models import RouteStation
        from django.core.paginator import Paginator
        
        page = request.GET.get('page', '1')
        route_stations = RouteStation.objects.filter(station__code=code).select_related('route__train').order_by('arrival_time')
        
        paginator = Paginator(route_stations, 10)
        try:
            p = paginator.page(page)
        except:
            p = paginator.page(1)
            
        data = []
        for rs in p.object_list:
            t = rs.route.train
            data.append({
                'train_number': t.number,
                'train_name': t.name,
                'train_type': t.train_type,
                'arrival_time': str(rs.arrival_time) if rs.arrival_time else None,
                'departure_time': str(rs.departure_time) if rs.departure_time else None,
            })
            
        return Response({
            'count': paginator.count,
            'next': p.has_next() if hasattr(p, 'has_next') else False,
            'previous': p.has_previous() if hasattr(p, 'has_previous') else False,
            'results': data
        })
