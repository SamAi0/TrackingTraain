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
        date_str = request.GET.get('date', '')
        
        if not source or not destination:
            return Response({'error': 'Source and destination are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get routes where the train stops at the source station
        source_stops = RouteStation.objects.filter(station__code__icontains=source).values_list('route_id', 'sequence_number', 'station__code', 'distance_from_source')
        
        # Get routes where the train stops at the destination station
        dest_stops = RouteStation.objects.filter(station__code__icontains=destination).values_list('route_id', 'sequence_number', 'station__code', 'distance_from_source')
        
        dest_dict = {r[0]: (r[1], r[2], r[3]) for r in dest_stops}
        
        valid_route_ids = []
        route_boundaries = {}
        for route_id, src_seq, src_code, src_dist in source_stops:
            if route_id in dest_dict:
                dest_seq, dest_code, dest_dist = dest_dict[route_id]
                if src_seq < dest_seq:
                    valid_route_ids.append(route_id)
                    route_boundaries[route_id] = (src_seq, dest_seq, src_dist, dest_dist)
                
        # Limit to first 50 matches for performance
        valid_route_ids = valid_route_ids[:50]
        trains = Train.objects.filter(route__id__in=valid_route_ids).select_related('route')
        
        import datetime
        day_of_week = None
        if date_str:
            try:
                dt = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                day_of_week = dt.strftime('%a').upper()[:3] # MON, TUE, etc.
            except ValueError:
                pass
        
        serializer = TrainSerializer(trains, many=True)
        response_data = serializer.data
        
        final_response_data = []
        
        # Enrich the response with intermediate stops and calculated distances
        for train_data in response_data:
            train_obj = next((t for t in trains if t.number == train_data['number']), None)
            if not train_obj or not hasattr(train_obj, 'route'):
                continue
                
            route_id = train_obj.route.id
            if route_id not in route_boundaries:
                continue
                
            # Filter by running_days if date is provided
            if day_of_week and train_obj.running_days:
                raw_days = train_obj.running_days.get('raw', '')
                if raw_days and raw_days != "NOT_SPECIFIED_IN_SOURCE":
                    # We have a specific day rule, we must check it.
                    # Formats from JSON:
                    # 'S M T W T F S' (space separated initials)
                    # 'MON-SAT_AC_SUN-HOLIDAY_NON_AC'
                    
                    runs_today = False
                    
                    # Convert day_of_week (e.g. 'SUN', 'MON') to initial for 'S M T W T F S' format
                    day_initials = {'SUN': 'S', 'MON': 'M', 'TUE': 'T', 'WED': 'W', 'THU': 'T', 'FRI': 'F', 'SAT': 'S'}
                    initial = day_initials.get(day_of_week)
                    
                    if ' ' in raw_days: # e.g. "S M T W T F S"
                        # Actually Thursday is 'T' and Tuesday is 'T'. Let's be careful.
                        # It's a sequence of 7 characters separated by space. 
                        # Order: S M T W T F S  (Sun Mon Tue Wed Thu Fri Sat)
                        # Let's map day of week to index
                        dow_idx = {'SUN': 0, 'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6}
                        parts = raw_days.split(' ')
                        if len(parts) == 7:
                            if parts[dow_idx[day_of_week]] != '-': # Assuming '-' means doesn't run
                                runs_today = True
                        else:
                            # If it's something else like "M W F", just check if initial is in it (imperfect but better than nothing)
                            if initial in parts:
                                runs_today = True
                    
                    elif "MON-SAT" in raw_days:
                        if day_of_week != 'SUN':
                            runs_today = True
                    else:
                        # Fallback for unknown reliable formats: include it so we don't drop blindly
                        runs_today = True
                        
                    if not runs_today:
                        continue # Skip this train because it doesn't run today
            src_seq, dest_seq, src_dist, dest_dist = route_boundaries[route_id]
            
            route_stations = RouteStation.objects.filter(
                route_id=route_id,
                sequence_number__gte=src_seq,
                sequence_number__lte=dest_seq
            ).select_related('station').order_by('sequence_number')
            
            segment_stations = []
            prev_distance = None
            
            total_journey_distance = None
            if dest_dist is not None and src_dist is not None:
                total_journey_distance = dest_dist - src_dist
                
            for rs in route_stations:
                dist_from_prev = None
                if prev_distance is not None and rs.distance_from_source is not None:
                    dist_from_prev = rs.distance_from_source - prev_distance
                    
                cum_dist = None
                if rs.distance_from_source is not None and src_dist is not None:
                    cum_dist = rs.distance_from_source - src_dist
                    
                halt_duration = None
                if rs.arrival_time and rs.departure_time:
                    arr_dt = datetime.datetime.combine(datetime.date.today(), rs.arrival_time)
                    dep_dt = datetime.datetime.combine(datetime.date.today(), rs.departure_time)
                    if dep_dt < arr_dt:
                        dep_dt += datetime.timedelta(days=1)
                    # Format halt_duration as HH:MM:SS or just minutes
                    diff_seconds = int((dep_dt - arr_dt).total_seconds())
                    hours, remainder = divmod(diff_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    halt_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                segment_stations.append({
                    'sequence': rs.sequence_number,
                    'station_name': rs.station.name,
                    'station_code': rs.station.code,
                    'distance_from_previous': dist_from_prev,
                    'cumulative_distance': cum_dist,
                    'arrival_time': rs.arrival_time.strftime('%H:%M:%S') if rs.arrival_time else None,
                    'departure_time': rs.departure_time.strftime('%H:%M:%S') if rs.departure_time else None,
                    'halt_duration': halt_duration
                })
                
                if rs.distance_from_source is not None:
                    prev_distance = rs.distance_from_source
                    
            train_data['total_journey_distance'] = total_journey_distance
            train_data['journey_segment'] = segment_stations
            
            is_complete = train_obj.running_days.get('timetable_complete', True) if train_obj.running_days else True
            train_data['timetable_complete'] = is_complete
            
            # The departure time is from the FIRST station in the segment
            train_data['departure_time'] = segment_stations[0]['departure_time'] if segment_stations else None
            # The arrival time is from the LAST station in the segment
            train_data['arrival_time'] = segment_stations[-1]['arrival_time'] if segment_stations else None
            
            final_response_data.append(train_data)

        return Response(final_response_data, status=status.HTTP_200_OK)

class FullRouteAPIView(APIView):
    def get(self, request, train_number):
        try:
            train = Train.objects.get(number=train_number)
            if not hasattr(train, 'route'):
                return Response({'error': 'Route not found for this train.'}, status=status.HTTP_404_NOT_FOUND)
            
            source = request.GET.get('source', '').upper()
            destination = request.GET.get('destination', '').upper()
            
            stations = train.route.stations.all().order_by('sequence_number')
            
            if source and destination:
                src_seq = None
                dst_seq = None
                for rs in stations:
                    if rs.station.code == source:
                        src_seq = rs.sequence_number
                    if rs.station.code == destination:
                        dst_seq = rs.sequence_number
                
                if src_seq is not None and dst_seq is not None and src_seq < dst_seq:
                    stations = stations.filter(sequence_number__gte=src_seq, sequence_number__lte=dst_seq)
            
            route_data = []
            for rs in stations:
                route_data.append({
                    'station_code': rs.station.code,
                    'station_name': rs.station.name,
                    'sequence_number': rs.sequence_number,
                    'distance': rs.distance_from_source,
                    'arrival_time': rs.arrival_time.strftime('%H:%M:%S') if rs.arrival_time else None,
                    'departure_time': rs.departure_time.strftime('%H:%M:%S') if rs.departure_time else None,
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
