from django.db.models import Prefetch, F
from routes.models import Route, RouteStation
from trains.models import Train
from stations.models import Station
import heapq
from datetime import datetime, timedelta

TRANSFER_BUFFER_MINUTES = 30

_graph_cache = None

def clear_graph_cache():
    global _graph_cache
    _graph_cache = None
    
    import os
    from django.conf import settings
    cache_file = os.path.join(settings.BASE_DIR, 'graph_cache.pkl')
    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
        except Exception:
            pass

import os
import pickle
from django.conf import settings

def get_graph():
    global _graph_cache
    if _graph_cache is not None:
        return _graph_cache
        
    cache_file = os.path.join(settings.BASE_DIR, 'graph_cache.pkl')
    
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            _graph_cache = pickle.load(f)
            return _graph_cache
            
    edges = RouteStation.objects.values(
        'route__train_id', 'station_id', 'sequence_number', 
        'distance_from_source', 'arrival_time', 'departure_time', 'journey_day'
    ).order_by('route__train_id', 'sequence_number')
    
    graph = {}
    prev_stop = None
    
    for stop in edges:
        stn = stop['station_id']
        if stn not in graph:
            graph[stn] = []
            
        if prev_stop and prev_stop['route__train_id'] == stop['route__train_id']:
            graph[prev_stop['station_id']].append({
                'to': stn,
                'train_id': stop['route__train_id'],
                'from_dep': prev_stop['departure_time'],
                'to_arr': stop['arrival_time'],
                'from_day': prev_stop['journey_day'],
                'to_day': stop['journey_day'],
                'dist': stop['distance_from_source'] - prev_stop['distance_from_source']
            })
            
        prev_stop = stop
        
    _graph_cache = graph
    
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(_graph_cache, f)
    except Exception:
        pass
        
    return _graph_cache

def time_to_minutes(t):
    if not t: return 0
    return t.hour * 60 + t.minute

def calculate_wait_time(arr_time, arr_day, dep_time, dep_day, is_same_train):
    # Returns wait time in minutes, or None if invalid
    if not arr_time or not dep_time:
        return 0 # Assume 0 if data missing, to not break completely, though technically risky.

    arr_total = (arr_day - 1) * 24 * 60 + time_to_minutes(arr_time)
    dep_total = (dep_day - 1) * 24 * 60 + time_to_minutes(dep_time)

    if is_same_train:
        if dep_total < arr_total:
            dep_total += 24 * 60 
        return max(0, dep_total - arr_total)
        
    arr_minutes = time_to_minutes(arr_time)
    dep_minutes = time_to_minutes(dep_time)
    
    if dep_minutes >= arr_minutes + TRANSFER_BUFFER_MINUTES:
        return dep_minutes - arr_minutes
    else:
        return (24 * 60 - arr_minutes) + dep_minutes

def find_direct_trains(src_code, dest_code):
    src_stations = RouteStation.objects.filter(station_id=src_code).select_related('route')
    dest_stations = RouteStation.objects.filter(station_id=dest_code).select_related('route')

    src_dict = {rs.route_id: rs for rs in src_stations}
    dest_dict = {rs.route_id: rs for rs in dest_stations}

    valid_route_ids = []
    for route_id, src_rs in src_dict.items():
        if route_id in dest_dict:
            dest_rs = dest_dict[route_id]
            if src_rs.sequence_number < dest_rs.sequence_number:
                valid_route_ids.append(route_id)

    trains = Train.objects.filter(route__id__in=valid_route_ids).select_related('source', 'destination')
    
    results = []
    for train in trains:
        route_id = train.route.id
        src_rs = src_dict[route_id]
        dest_rs = dest_dict[route_id]

        results.append({
            "train_number": train.number,
            "train_name": train.name,
            "departure": src_rs.departure_time.strftime("%H:%M") if src_rs.departure_time else None,
            "arrival": dest_rs.arrival_time.strftime("%H:%M") if dest_rs.arrival_time else None,
            "distance_km": dest_rs.distance_from_source - src_rs.distance_from_source,
            "running_days": train.running_days
        })
    return results

def get_route_timeline(train_number, src_code, dest_code):
    try:
        route = Route.objects.get(train_id=train_number)
    except Route.DoesNotExist:
        return None

    all_stations = list(RouteStation.objects.filter(route=route).select_related('station').order_by('sequence_number'))
    
    src_idx = dest_idx = -1
    for i, rs in enumerate(all_stations):
        if rs.station_id == src_code: src_idx = i
        if rs.station_id == dest_code: dest_idx = i
            
    if src_idx == -1 or dest_idx == -1 or src_idx >= dest_idx:
        return None

    segment = all_stations[src_idx:dest_idx+1]
    
    stations_data = []
    for i, rs in enumerate(segment):
        stations_data.append({
            "station_code": rs.station_id,
            "station_name": rs.station.name,
            "sequence": rs.sequence_number,
            "distance_from_start": rs.distance_from_source - segment[0].distance_from_source,
            "arrival_time": rs.arrival_time.strftime("%H:%M") if rs.arrival_time else None,
            "departure_time": rs.departure_time.strftime("%H:%M") if rs.departure_time else None,
            "journey_day": rs.journey_day
        })
        
    return {
        "train_number": train_number,
        "from": segment[0].station.name,
        "to": segment[-1].station.name,
        "total_distance_km": segment[-1].distance_from_source - segment[0].distance_from_source,
        "station_count": len(segment),
        "stations": stations_data
    }

def find_multi_train_route(src_code, dest_code):
    graph = get_graph()
    if src_code not in graph or dest_code not in graph:
        return None
        
    queue = []
    for edge in graph[src_code]:
        heapq.heappush(queue, (
            (0, 0), 
            edge['to'], 
            edge['train_id'],
            edge['to_arr'],
            edge['to_day'],
            [(src_code, edge['train_id'], edge['from_dep'], edge['from_day'], 0, edge['from_dep'])],
            edge['dist']
        ))
        
    visited = set()
    
    while queue:
        (transfers, total_mins), current_node, current_train, arr_time, arr_day, path, total_dist = heapq.heappop(queue)
        
        state_key = (current_node, current_train)
        if state_key in visited:
            continue
        visited.add(state_key)
        
        path = path + [(current_node, current_train, arr_time, arr_day, total_dist, arr_time)]
        
        if current_node == dest_code:
            return build_multi_train_response(path, total_mins, transfers, total_dist)
            
        for edge in graph.get(current_node, []):
            next_node = edge['to']
            next_train = edge['train_id']
            
            is_same_train = (current_train == next_train)
            wait_time = calculate_wait_time(arr_time, arr_day, edge['from_dep'], edge['from_day'], is_same_train)
            travel_time = calculate_wait_time(edge['from_dep'], edge['from_day'], edge['to_arr'], edge['to_day'], True)
            
            if wait_time is None or travel_time is None:
                continue
                
            new_transfers = transfers if is_same_train else transfers + 1
            new_total_mins = total_mins + wait_time + travel_time
            new_dist = total_dist + edge['dist']
            
            # Store departure time for the transfer
            dep_for_next = edge['from_dep'] if not is_same_train else None
            
            heapq.heappush(queue, (
                (new_transfers, new_total_mins),
                next_node,
                next_train,
                edge['to_arr'],
                edge['to_day'],
                path[:-1] + [(current_node, current_train, arr_time, arr_day, total_dist, dep_for_next)],
                new_dist
            ))
            
    return None

def build_multi_train_response(path, total_mins, transfers, total_dist):
    segments = []
    
    current_train = path[1][1]
    segment_start_idx = 0
    
    for i in range(1, len(path)):
        node, train, time, day, dist, next_dep = path[i]
        
        if train != current_train or i == len(path) - 1:
            end_idx = i if train == current_train else i - 1
            
            seg_src = path[segment_start_idx][0]
            seg_dest = path[end_idx][0]
            
            timeline = get_route_timeline(current_train, seg_src, seg_dest)
            
            segments.append({
                "type": "train",
                "train_number": current_train,
                "from": seg_src,
                "to": seg_dest,
                "distance_km": path[end_idx][4] - path[segment_start_idx][4],
                "departure_time": path[segment_start_idx][2].strftime("%H:%M") if path[segment_start_idx][2] else None,
                "arrival_time": path[end_idx][2].strftime("%H:%M") if path[end_idx][2] else None,
                "stops": timeline['stations'] if timeline else []
            })
            
            if train != current_train:
                arr_time = path[end_idx][2]
                dep_time = path[end_idx][5]
                
                segments.append({
                    "type": "transfer",
                    "station": seg_dest,
                    "arrival_time": arr_time.strftime("%H:%M") if arr_time else None,
                    "next_departure_time": dep_time.strftime("%H:%M") if dep_time else None
                })
                
                current_train = train
                segment_start_idx = end_idx
                
    return {
        "success": True,
        "route_type": "multi_train" if transfers > 0 else "direct",
        "source": path[0][0],
        "destination": path[-1][0],
        "total_distance_km": total_dist,
        "total_duration_min": total_mins,
        "transfers": transfers,
        "segments": segments
    }
