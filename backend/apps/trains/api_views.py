import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, F, OuterRef, Subquery, IntegerField, CharField, TimeField
from .models import Train
from routes.models import RouteStation
from stations.models import Station

class TrainSearchAPIView(APIView):
    def get(self, request):
        source = request.GET.get('source', '').strip()
        destination = request.GET.get('destination', '').strip()
        
        if not source or not destination:
            return Response({'error': 'Source and destination are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Optimize search using Subqueries to avoid N+1 and Python loops
        # We need trains where RouteStation(source) sequence < RouteStation(destination) sequence
        
        # We allow search by name or code, so let's resolve them to codes first
        try:
            src_station = Station.objects.get(Q(code__iexact=source) | Q(name__iexact=source))
            source_code = src_station.code
            dst_station = Station.objects.get(Q(code__iexact=destination) | Q(name__iexact=destination))
            dest_code = dst_station.code
        except Station.DoesNotExist:
            return Response([], status=status.HTTP_200_OK) # Return empty if station not found
        except Station.MultipleObjectsReturned:
            # If name matches multiple, just pick first for simplicity or strictly match
            src_station = Station.objects.filter(Q(code__iexact=source) | Q(name__iexact=source)).first()
            source_code = src_station.code
            dst_station = Station.objects.filter(Q(code__iexact=destination) | Q(name__iexact=destination)).first()
            dest_code = dst_station.code

        source_stops = RouteStation.objects.filter(
            route_id=OuterRef('route__id'),
            station_id=source_code
        )
        dest_stops = RouteStation.objects.filter(
            route_id=OuterRef('route__id'),
            station_id=dest_code
        )

        trains = Train.objects.select_related('route').annotate(
            src_seq=Subquery(source_stops.values('sequence_number')[:1], output_field=IntegerField()),
            dst_seq=Subquery(dest_stops.values('sequence_number')[:1], output_field=IntegerField()),
            dep_time=Subquery(source_stops.values('departure_time')[:1], output_field=TimeField()),
            arr_time=Subquery(dest_stops.values('arrival_time')[:1], output_field=TimeField()),
            src_day=Subquery(source_stops.values('journey_day')[:1], output_field=IntegerField()),
            dst_day=Subquery(dest_stops.values('journey_day')[:1], output_field=IntegerField())
        ).filter(
            src_seq__isnull=False, 
            dst_seq__isnull=False, 
            src_seq__lt=F('dst_seq')
        ).order_by('dep_time')[:50]

        final_response_data = []
        for train in trains:
            # Calculate duration
            halt_duration = None
            if train.arr_time and train.dep_time:
                dep_dt = datetime.datetime.combine(datetime.date.today(), train.dep_time)
                arr_dt = datetime.datetime.combine(datetime.date.today(), train.arr_time)
                
                # Adjust for journey days
                day_diff = (train.dst_day or 1) - (train.src_day or 1)
                arr_dt += datetime.timedelta(days=day_diff)
                
                if arr_dt < dep_dt:
                    arr_dt += datetime.timedelta(days=1)
                
                diff_seconds = int((arr_dt - dep_dt).total_seconds())
                hours, remainder = divmod(diff_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                halt_duration = f"{hours:02d}h {minutes:02d}m"
            
            final_response_data.append({
                'number': train.number,
                'name': train.name,
                'train_type': train.train_type,
                'source': src_station.name,
                'source_code': source_code,
                'destination': dst_station.name,
                'destination_code': dest_code,
                'departure_time': train.dep_time.strftime('%H:%M:%S') if train.dep_time else None,
                'arrival_time': train.arr_time.strftime('%H:%M:%S') if train.arr_time else None,
                'duration': halt_duration,
                'running_days': 'NOT_SPECIFIED_IN_SOURCE'
            })

        return Response(final_response_data, status=status.HTTP_200_OK)


class FullRouteAPIView(APIView):
    def get(self, request, train_number):
        try:
            train = Train.objects.get(number=train_number)
            if not hasattr(train, 'route'):
                return Response({'error': 'Route not found for this train.'}, status=status.HTTP_404_NOT_FOUND)
            
            # Use select_related to prevent N+1 queries when accessing station coordinates
            stations = train.route.stations.select_related('station').order_by('sequence_number')
            
            route_data = []
            for rs in stations:
                # Calculate halt duration if applicable
                halt = None
                if rs.arrival_time and rs.departure_time:
                    arr_dt = datetime.datetime.combine(datetime.date.today(), rs.arrival_time)
                    dep_dt = datetime.datetime.combine(datetime.date.today(), rs.departure_time)
                    if dep_dt < arr_dt:
                        dep_dt += datetime.timedelta(days=1)
                    diff_seconds = int((dep_dt - arr_dt).total_seconds())
                    hours, remainder = divmod(diff_seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    if hours > 0 or minutes > 0:
                        halt = f"{hours:02d}h {minutes:02d}m" if hours > 0 else f"{minutes:02d}m"

                route_data.append({
                    'station_code': rs.station.code,
                    'station_name': rs.station.name,
                    'sequence_number': rs.sequence_number,
                    'arrival_time': rs.arrival_time.strftime('%H:%M') if rs.arrival_time else None,
                    'departure_time': rs.departure_time.strftime('%H:%M') if rs.departure_time else None,
                    'halt_duration': halt,
                    'day': rs.journey_day,
                    'latitude': rs.station.latitude,
                    'longitude': rs.station.longitude
                })
                
            return Response({
                'train_number': train.number, 
                'train_name': train.name, 
                'train_type': train.train_type,
                'source': route_data[0]['station_name'] if route_data else None,
                'destination': route_data[-1]['station_name'] if route_data else None,
                'route': route_data
            }, status=status.HTTP_200_OK)
        except Train.DoesNotExist:
            return Response({'error': 'Train not found.'}, status=status.HTTP_404_NOT_FOUND)


class TrainAutocompleteAPIView(APIView):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        
        data = []
        if not q:
            return Response(data, status=status.HTTP_200_OK)
            
        # Fast local DB search
        trains = Train.objects.filter(
            Q(number__icontains=q) | 
            Q(name__icontains=q)
        ).order_by('number')[:10]
        
        for tr in trains:
            data.append({
                'number': tr.number,
                'name': tr.name,
                'is_external': False
            })
            
        return Response(data, status=status.HTTP_200_OK)
