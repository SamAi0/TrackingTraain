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
        from django.db.models.functions import Coalesce
        # Sort by time of day. Coalesce ensures origin stations (null arrival) sort by departure
        qs = RouteStation.objects.filter(station__code=code).select_related('route__train').order_by(
            Coalesce('arrival_time', 'departure_time')
        )
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request)
        
        data = []
        for rs in page:
            train = rs.route.train
            data.append({
                'train_number': train.number,
                'train_name': train.name,
                'train_type': train.normalized_type,
                'arrival_time': rs.arrival_time,
                'departure_time': rs.departure_time,
                'distance': rs.distance_from_source,
                'journey_day': rs.journey_day,
                'source': train.source.code,
                'destination': train.destination.code
            })
            
        return paginator.get_paginated_response(data)
