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
        from railway_api.services.train_service import TrainService
        source = request.GET.get('source', '').strip()
        destination = request.GET.get('destination', '').strip()
        date = request.GET.get('date', '').strip()
        
        if not source or not destination:
            return Response({'error': 'Source and destination are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        result = TrainService.trains_between(source, destination, date)
        
        if result.get('success'):
            data_list = result.get('data', [])
            # Map the fields back to what the frontend expects
            final_response_data = []
            for tr in data_list:
                final_response_data.append({
                    'number': tr.get('number'),
                    'name': tr.get('name'),
                    'train_type': tr.get('type', 'EXPRESS'),
                    'source': tr.get('source'),
                    'source_code': tr.get('source'),
                    'destination': tr.get('destination'),
                    'destination_code': tr.get('destination'),
                    'departure_time': tr.get('departure_time'),
                    'arrival_time': tr.get('arrival_time'),
                    'duration': tr.get('duration'),
                    'running_days': 'NOT_SPECIFIED_IN_SOURCE'
                })
            return Response(final_response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': result.get('error', 'Failed to search trains')}, status=status.HTTP_400_BAD_REQUEST)


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
        from railway_api.services.train_service import TrainService
        q = request.GET.get('q', '').strip()
        
        result = TrainService.search_train(q)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)
