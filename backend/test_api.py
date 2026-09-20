import os, sys, django, requests
sys.path.append('c:/Users/Asus/Desktop/Personal/rgc lcg/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def run_tests():
    base_url = 'http://127.0.0.1:8000/api/trains/search/'
    
    with open('test_results.md', 'w') as f:
        f.write('# API Test Results\n\n')
        
        # Test 1: CSMT to PNVL (Check services and incomplete data)
        res = requests.get(f'{base_url}?source=CSMT&destination=PNVL')
        data = res.json()
        f.write('## Test 1: CSMT to PNVL\n')
        f.write(f'Found {len(data)} trains.\n')
        for t in data:
            f.write(f'- Train {t["number"]} ({t["name"]}) [Complete: {t.get("timetable_complete")}]\n')
            f.write(f'  Departure: {t.get("departure_time")} | Arrival: {t.get("arrival_time")}\n')
        
        # Test 2: PNVL to CSMT (Reverse direction, should NOT return the above)
        res = requests.get(f'{base_url}?source=PNVL&destination=CSMT')
        data = res.json()
        f.write('\n## Test 2: PNVL to CSMT (Reverse direction check)\n')
        f.write(f'Found {len(data)} trains.\n')
        for t in data:
            f.write(f'- Train {t["number"]} ({t["name"]}) [Complete: {t.get("timetable_complete")}]\n')
        
        # Test 3: Running day filter for 98045 (MON-SAT_AC_SUN-HOLIDAY_NON_AC)
        # 2026-09-20 is a Sunday. 98045 should NOT appear if we filter by MON-SAT properly, 
        # but wait, our parser checks "MON-SAT" and sets it to not run on SUN. Let's verify.
        res = requests.get(f'{base_url}?source=CSMT&destination=PNVL&date=2026-09-20')
        data = res.json()
        f.write('\n## Test 3: CSMT to PNVL on a Sunday\n')
        f.write(f'Found {len(data)} trains.\n')
        for t in data:
            f.write(f'- Train {t["number"]} ({t["name"]})\n')

        # Test 4: Running day filter for 98045 on a Monday (2026-09-21)
        res = requests.get(f'{base_url}?source=CSMT&destination=PNVL&date=2026-09-21')
        data = res.json()
        f.write('\n## Test 4: CSMT to PNVL on a Monday\n')
        f.write(f'Found {len(data)} trains.\n')
        for t in data:
            f.write(f'- Train {t["number"]} ({t["name"]})\n')
            
        # Test 5: PNVL to TNA (Test incomplete service)
        res = requests.get(f'{base_url}?source=PNVL&destination=TNA')
        data = res.json()
        f.write('\n## Test 5: PNVL to TNA\n')
        f.write(f'Found {len(data)} trains.\n')
        for t in data:
            f.write(f'- Train {t["number"]} ({t["name"]}) [Complete: {t.get("timetable_complete")}]\n')

run_tests()
