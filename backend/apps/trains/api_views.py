from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Train
from .serializers import TrainSerializer

from routes.models import RouteStation

class TrainSearchAPIView(APIView):
    def get(self, request):
        source = request.GET.get('source', '').upper()
        destination = request.GET.get('destination', '').upper()
        
        if not source or not destination:
            return Response({'error': 'Source and destination are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get routes where the train stops at the source station
        source_stops = RouteStation.objects.filter(station__code__icontains=source).values_list('route_id', 'sequence_number', 'station__code')
        
        # Get routes where the train stops at the destination station
        dest_stops = RouteStation.objects.filter(station__code__icontains=destination).values_list('route_id', 'sequence_number', 'station__code')
        
        dest_dict = {r[0]: r[1] for r in dest_stops}
        
        valid_route_ids = []
        for route_id, src_seq, src_code in source_stops:
            if route_id in dest_dict and src_seq < dest_dict[route_id]:
                valid_route_ids.append(route_id)
                
        # Limit to first 50 matches for performance
        trains = Train.objects.filter(route__id__in=valid_route_ids)[:50]
        
        serializer = TrainSerializer(trains, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FullRouteAPIView(APIView):
    def get(self, request, train_number):
        try:
            train = Train.objects.get(number=train_number)
            if not hasattr(train, 'route'):
                return Response({'error': 'Route not found for this train.'}, status=status.HTTP_404_NOT_FOUND)
            
            stations = train.route.stations.all().order_by('sequence_number')
            route_data = []
            for rs in stations:
                route_data.append({
                    'station_code': rs.station.code,
                    'station_name': rs.station.name,
                    'sequence_number': rs.sequence_number,
                    'distance': rs.distance_from_source
                })
            return Response({'train_number': train.number, 'train_name': train.name, 'route': route_data}, status=status.HTTP_200_OK)
        except Train.DoesNotExist:
            return Response({'error': 'Train not found.'}, status=status.HTTP_404_NOT_FOUND)

MUMBAI_TRAIN_NUMBERS = ['12951', '12952', '12953', '12954', '12123', '12124', '12127', '12128']

class TrainAutocompleteAPIView(APIView):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        
        data = []
        if not q:
            return Response(data, status=status.HTTP_200_OK)
            
        from trains.services.rapidapi_service import RapidAPIService
        rapid_service = RapidAPIService()
        result = rapid_service.search_train(q)
        
        if result.get('status_code') == 200:
            for item in result.get('data', [])[:10]:
                data.append({
                    'number': item.get('number'),
                    'name': item.get('name'),
                    'is_external': True
                })
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'error': result.get('error', 'External service failed')}, status=result.get('status_code', 500))
