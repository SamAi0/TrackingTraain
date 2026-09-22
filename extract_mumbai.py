import json

with open('mumbai_suburban_timetable_trackease.json', 'r') as f:
    data = json.load(f)

samples = data.get('service_samples', [])

print("### Available Mumbai Local Train Services\n")
print("| Train Number | Train Name | Railway Line | Type | Source | Dest | Dep | Arr | Stops | Test Purpose |")
print("|---|---|---|---|---|---|---|---|---|---|")

results = []
valid = 0
incomplete = 0
missing_intermediate = 0

for s in samples:
    num = s.get('service_number', 'N/A')
    name = s.get('service_name', 'N/A')
    line = s.get('line', 'Unknown')
    t_type = s.get('service_type', 'NORMAL')
    src_code = s.get('origin', 'N/A')
    dst_code = s.get('destination', 'N/A')
    src = src_code # name might be in station_master
    dst = dst_code
    dep = s.get('origin_departure', '--:--') or '--:--'
    arr = s.get('destination_arrival', '--:--') or '--:--'
    
    # Check intermediate
    route_stops = s.get('route_stops', [])
    # wait, earlier it was 0 for route_stops. Let's see if there is another key.
    
    stops = len(route_stops) if route_stops else 'N/A'
    if not route_stops: missing_intermediate += 1
    
    if dep == '--:--' or arr == '--:--':
        incomplete += 1
        
    valid += 1
    
    purpose = "End-to-End"
    if not route_stops: purpose += " (Missing Intermediate)"
    if t_type == 'FAST': purpose = "Fast Skipping"
    if t_type == 'AC LOCAL': purpose = "AC Local Testing"
    
    results.append({
        'num': num, 'name': name, 'line': line, 'type': t_type,
        'src': src, 'src_code': src_code, 'dst': dst, 'dst_code': dst_code,
        'dep': dep, 'arr': arr, 'stops': stops, 'purpose': purpose
    })
    
    print(f"| {num} | {name} | {line} | {t_type} | {src} ({src_code}) | {dst} ({dst_code}) | {dep} | {arr} | {stops} | {purpose} |")

print("\n### Recommended Mumbai Local Testing Cases")
print("These are specifically selected from the available data for testing TrackEase features:\n")

lines_covered = set(r['line'] for r in results)
for line in lines_covered:
    best = next((r for r in results if r['line'] == line), None)
    if best:
        print(f"- **{line} Line**: `{best['num']}` ({best['src_code']} to {best['dst_code']}) - Ideal for {best['purpose']}.")

print(f"\n**Summary Report:**")
print(f"- Total local services found: {valid}")
print(f"- Total stations found: {len(data.get('station_master', []))}")
print(f"- Lines represented: {', '.join(lines_covered)}")
print(f"- Source file: `mumbai_suburban_timetable_trackease.json`")
print(f"- Services with incomplete intermediate timings: {missing_intermediate}")
