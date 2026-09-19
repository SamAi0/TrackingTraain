import json
data = json.load(open('../trains.json'))
for t in data:
    if t.get('trainNumber') == '12260':
        print(f"Source: {t.get('source', {}).get('code')}, Dest: {t.get('destination', {}).get('code')}")
        route = t.get('completeOrderedRoute', [])
        ndls_stops = [h for h in route if h.get('stationCode') == 'NDLS']
        print("NDLS stop in JSON:", ndls_stops)
        break
