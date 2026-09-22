import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from trains.models import Train

class LiveTrackingAPIView(APIView):
    def get(self, request, train_number):
        try:
            train = Train.objects.get(number=train_number)
            if not hasattr(train, 'route'):
                return Response({'error': 'Route not found for this train.'}, status=status.HTTP_404_NOT_FOUND)
                
            demo_delay = int(request.GET.get('demo_delay', 0))
            
            # Fetch all route stations ordered by sequence
            stations = list(train.route.stations.select_related('station').order_by('sequence_number'))
            if not stations:
                return Response({'error': 'No stations on this route.'}, status=status.HTTP_404_NOT_FOUND)
                
            now = datetime.datetime.now()
            today = datetime.date.today()
            
            # For deterministic simulation, we assume the train started its journey on 'today' minus its first day
            # Actually, to make it currently running, we just compare current time against schedule.
            
            source_station = stations[0]
            destination_station = stations[-1]
            
            # Base departure datetime from source
            if source_station.departure_time:
                base_start_time = source_station.departure_time
            elif source_station.arrival_time:
                base_start_time = source_station.arrival_time
            else:
                base_start_time = datetime.time(0, 0)
                
            base_start_dt = datetime.datetime.combine(today, base_start_time)
            
            # Add demo delay to base start dt for the simulation reality
            delay_td = datetime.timedelta(minutes=demo_delay)
            
            # Calculate absolute datetimes for all stations
            route_details = []
            
            for idx, rs in enumerate(stations):
                day_offset = (rs.journey_day or 1) - (source_station.journey_day or 1)
                
                # Arrival
                if rs.arrival_time:
                    arr_dt = datetime.datetime.combine(today, rs.arrival_time) + datetime.timedelta(days=day_offset)
                    # Handle crossing midnight if arrival is before base_start_time but on same day offset
                    # The timetable assumes sequential times.
                    if idx > 0 and arr_dt < route_details[idx-1]['sim_dep_dt']:
                        arr_dt += datetime.timedelta(days=1)
                else:
                    arr_dt = route_details[idx-1]['sim_dep_dt'] if idx > 0 else base_start_dt
                
                # Departure
                if rs.departure_time:
                    dep_dt = datetime.datetime.combine(arr_dt.date(), rs.departure_time)
                    if dep_dt < arr_dt:
                        dep_dt += datetime.timedelta(days=1)
                else:
                    dep_dt = arr_dt
                    
                route_details.append({
                    'rs': rs,
                    'sim_arr_dt': arr_dt,
                    'sim_dep_dt': dep_dt,
                    'exp_arr_dt': arr_dt + delay_td,
                    'exp_dep_dt': dep_dt + delay_td,
                    'is_first': idx == 0,
                    'is_last': idx == len(stations) - 1,
                    'index': idx
                })
            
            # Determine current state
            # A train is at a station if now >= exp_arr_dt and now <= exp_dep_dt
            # A train is between stations if now > prev_exp_dep_dt and now < next_exp_arr_dt
            
            current_state = 'NOT_STARTED'
            current_idx = 0
            
            actual_end_time = route_details[-1]['exp_arr_dt']
            
            if now < route_details[0]['exp_dep_dt']:
                current_state = 'NOT_STARTED'
                current_idx = 0
            elif now > actual_end_time:
                current_state = 'COMPLETED'
                current_idx = len(stations) - 1
            else:
                # Find exactly where it is
                for i in range(len(route_details)):
                    r = route_details[i]
                    if r['exp_arr_dt'] <= now <= r['exp_dep_dt']:
                        current_state = 'AT_STATION'
                        current_idx = i
                        break
                    
                    if i < len(route_details) - 1:
                        next_r = route_details[i+1]
                        if r['exp_dep_dt'] < now < next_r['exp_arr_dt']:
                            current_state = 'IN_TRANSIT'
                            current_idx = i + 1 # Headed to next station
                            break
                            
            # Compute previous, current, next
            if current_state == 'NOT_STARTED':
                prev_stn = None
                curr_stn = stations[0]
                next_stn = stations[1] if len(stations) > 1 else None
                progress_pct = 0.0
                status_msg = 'DELAYED' if demo_delay > 0 else 'ON_TIME'
            elif current_state == 'COMPLETED':
                prev_stn = stations[-2] if len(stations) > 1 else None
                curr_stn = stations[-1]
                next_stn = None
                progress_pct = 100.0
                status_msg = 'COMPLETED'
            else:
                curr_stn = stations[current_idx]
                prev_stn = stations[current_idx - 1] if current_idx > 0 else None
                next_stn = stations[current_idx + 1] if current_idx < len(stations) - 1 else None
                
                # Progress based on sequence index
                progress_pct = round((current_idx / (len(stations) - 1)) * 100, 1) if len(stations) > 1 else 0
                
                if current_state == 'AT_STATION':
                    status_msg = 'HALTED' if demo_delay > 0 else 'ON_TIME'
                else:
                    status_msg = 'DELAYED' if demo_delay > 0 else 'ON_TIME'
            
            # Format route array
            formatted_route = []
            for i, r in enumerate(route_details):
                if i < current_idx:
                    route_status = 'COMPLETED'
                elif i == current_idx:
                    route_status = 'CURRENT'
                else:
                    route_status = 'UPCOMING'
                    
                formatted_route.append({
                    'station_name': r['rs'].station.name,
                    'station_code': r['rs'].station.code,
                    'sequence_number': r['rs'].sequence_number,
                    'status': route_status,
                    'arrival_time': r['rs'].arrival_time.strftime('%H:%M') if r['rs'].arrival_time else None,
                    'departure_time': r['rs'].departure_time.strftime('%H:%M') if r['rs'].departure_time else None,
                    'expected_arrival': r['exp_arr_dt'].strftime('%H:%M'),
                    'expected_departure': r['exp_dep_dt'].strftime('%H:%M'),
                    'latitude': r['rs'].station.latitude,
                    'longitude': r['rs'].station.longitude,
                    'day': r['rs'].journey_day
                })
                
            # Current station timings
            curr_r = route_details[current_idx]
            
            response_data = {
                'train_number': train.number,
                'train_name': train.name,
                'train_type': train.train_type,
                'status': status_msg,
                'delay_minutes': demo_delay,
                'previous_station': prev_stn.station.name if prev_stn else None,
                'current_station': curr_stn.station.name,
                'next_station': next_stn.station.name if next_stn else None,
                'expected_arrival': curr_r['exp_arr_dt'].strftime('%H:%M'),
                'expected_departure': curr_r['exp_dep_dt'].strftime('%H:%M'),
                'progress_percentage': progress_pct,
                'last_updated': now.isoformat(),
                'route': formatted_route
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Train.DoesNotExist:
            return Response({'error': 'Train not found.'}, status=status.HTTP_404_NOT_FOUND)

class FrontendActivityAPIView(APIView):
    def post(self, request):
        from utils.supabase_logger import SupabaseLogger
        activity_type = request.data.get('activity_type')
        user_id = request.user.id if request.user.is_authenticated else None
        
        if not activity_type:
            return Response({'error': 'activity_type is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        SupabaseLogger.log_activity(
            user_id=user_id,
            activity_type=activity_type,
            from_station=request.data.get('from_station'),
            to_station=request.data.get('to_station'),
            train_number=request.data.get('train_number'),
            booking_id=request.data.get('booking_id'),
            pnr=request.data.get('pnr'),
            metadata=request.data.get('metadata')
        )
        return Response({'success': True}, status=status.HTTP_200_OK)
