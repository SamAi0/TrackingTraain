import os
import sys
import json
import django
from collections import Counter

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from trains.models import Train
from stations.models import Station

data_file = 'data/mumbai_suburban/trans_harbour_line_2024_clean.json'
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    
services = data.get('services', [])

service_numbers = [s['service_number'] for s in services]
unique_services = set(service_numbers)
counter = Counter(service_numbers)
duplicates = [num for num, count in counter.items() if count > 1]

# Check existing trains in MySQL
existing_trains = list(Train.objects.filter(number__in=service_numbers))

# Station generation logic
unique_stations = set()
for s in services:
    for st in s['stations']:
        unique_stations.add(st['station_name'])
        
station_results = []
for name in unique_stations:
    db_stations = list(Station.objects.filter(name__iexact=name))
    if len(db_stations) == 1:
        # Matches existing
        continue
    elif len(db_stations) > 1:
        station_results.append({
            "name": name,
            "code": "N/A",
            "issue": f"Ambiguous existing matches: {[s.code for s in db_stations]}"
        })
    else:
        # Will be generated
        code = name.upper().replace(' ', '')[:20]
        # Check if code exists
        code_exists = Station.objects.filter(code=code).exists()
        # Check if similar name exists
        similar = list(Station.objects.filter(name__icontains=name[:5]))
        station_results.append({
            "name": name,
            "code": code,
            "code_exists": code_exists,
            "similar": [f"{s.name} ({s.code})" for s in similar]
        })

report = f"""# Trans Harbour 2024 Final Validation

## Train / Service Validation
- **Total Services Evaluated**: {len(services)}
- **Unique Service Count**: {len(unique_services)}
- **Duplicate Service Count**: {len(duplicates)}
"""

if duplicates:
    report += f"- **Duplicate Service Numbers**: {', '.join(duplicates)}\n"
    report += "- **Recommendation**: TrackEase `Train` model uses `number` as the primary key. If a service number appears twice (e.g. for Up and Down directions), importing them as separate `Train` records will cause a Primary Key violation or overwrite. Since duplicate count is > 0, the importer must be updated to handle this (e.g. suffixing direction to the train number or skipping).\n"
    ready = False
else:
    report += "- **Recommendation**: No duplicate service numbers found. Each service safely maps to exactly one `Train` record, one `Route`, and a set of `Schedule`/`RouteStation` entries.\n"
    ready = True

report += f"\n- **Proposed Train count**: {len(unique_services)}\n"
report += f"- **Existing Train Conflicts in MySQL**: {len(existing_trains)}\n"
if existing_trains:
    report += "- **Conflicts Details**: " + ", ".join([f"{t.number} ({t.name})" for t in existing_trains]) + "\n"

report += "\n## Station Mapping Validation\n"
for res in station_results:
    if "issue" in res:
        report += f"- **{res['name']}**: {res['issue']}\n"
    else:
        report += f"- **{res['name']}** -> Code: `{res['code']}`"
        if res['code_exists']:
            report += " ⚠️ CODE ALREADY EXISTS IN DB!"
            ready = False
        else:
            report += " (Code safe)."
            
        if res['similar']:
            report += f" Similar names in DB: {', '.join(res['similar'])}"
        report += "\n"

if ready:
    report += "\n## Final Recommendation\n**READY_FOR_IMPORT = YES**\n"
else:
    report += "\n## Final Recommendation\n**READY_FOR_IMPORT = NO**\n"

with open('C:/Users/Asus/.gemini/antigravity-ide/brain/8584ac8c-7413-4635-b3b4-726ecc23a9fb/trackease_trans_harbour_2024_final_validation.md', 'w', encoding='utf-8') as f:
    f.write(report)
    
print("Validation complete. Report written.")
