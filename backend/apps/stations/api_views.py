from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Case, When, Value, IntegerField
from .models import Station

class StationAutocompleteAPIView(APIView):
    def get(self, request):
        q = request.GET.get('q', '').strip().upper()
        
        if not q:
            # Default to some major Maharashtra stations if no query
            stations = Station.objects.filter(state__icontains='maharashtra')[:20]
        else:
            # Prioritize: 1. Exact code, 2. Exact name, 3. Prefix code, 4. Prefix name, 5. Contains
            stations = Station.objects.filter(
                Q(name__icontains=q) | Q(code__icontains=q)
            ).annotate(
                relevance=Case(
                    When(code__iexact=q, then=Value(1)),
                    When(name__iexact=q, then=Value(2)),
                    When(code__istartswith=q, then=Value(3)),
                    When(name__istartswith=q, then=Value(4)),
                    When(state__icontains='maharashtra', then=Value(5)),
                    default=Value(6),
                    output_field=IntegerField(),
                )
            ).order_by('relevance', 'name')[:20]
        
        data = []
        for s in stations[:10]:
            data.append({
                'code': s.code,
                'name': s.name
            })
            
        return Response(data, status=status.HTTP_200_OK)

from rest_framework.pagination import PageNumberPagination
from routes.models import RouteStation

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class StationListAPIView(APIView):
    def get(self, request):
        qs = Station.objects.all().order_by('name')
        
        zone = request.GET.get('zone', '').strip()
        state = request.GET.get('state', '').strip()
        q = request.GET.get('q', '').strip()
        
        if zone:
            qs = qs.filter(zone__iexact=zone)
        if state:
            qs = qs.filter(state__iexact=state)
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q) | Q(city__icontains=q))
            
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        
        data = []
        for s in page:
            data.append({
                'code': s.code,
                'name': s.name,
                'city': s.city,
                'state': s.state,
                'zone': s.zone,
                'address': s.address
            })
            
        return paginator.get_paginated_response(data)

class StationGeoAPIView(APIView):
    def get(self, request):
        # Lightweight for Leaflet map (only non-null coords within rough India bounds)
        qs = Station.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).filter(
            latitude__gt=6, latitude__lt=38,
            longitude__gt=68, longitude__lt=98
        )
        data = list(qs.values('code', 'name', 'latitude', 'longitude'))
        return Response(data)

class StationTrainsAPIView(APIView):
    def get(self, request, code):
        to_code = request.query_params.get('to')
        hours = request.query_params.get('hours', '1')
        from trains.services.rapidapi_service import RapidAPIService
        rapid_service = RapidAPIService()
        result = rapid_service.get_live_station(code, to_stn_code=to_code, hours=hours)
        
        if result.get('status_code') == 200:
            data = []
            for item in result.get('data', []):
                # RapidAPI provides schedule.arrival_time and schedule.departure_time
                # Map these to arrival_time and departure_time directly for the frontend
                data.append({
                    'train_number': item.get('number'),
                    'train_name': item.get('name'),
                    'train_type': item.get('train_type', 'UNKNOWN'),
                    'arrival_time': item.get('schedule', {}).get('arrival_time'),
                    'departure_time': item.get('schedule', {}).get('departure_time'),
                    'distance': 0,
                    'journey_day': 1,
                    'source': 'N/A',
                    'destination': 'N/A'
                })
            return Response({'results': data, 'count': len(data), 'next': None, 'previous': None}, status=status.HTTP_200_OK)
        else:
            return Response({'error': result.get('error', 'External service failed')}, status=result.get('status_code', 500))
