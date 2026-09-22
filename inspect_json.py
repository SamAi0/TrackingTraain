import json

with open('trackease_mumbai_navi_relevant_subset.json', 'r') as f:
    data = json.load(f)

print(f"Type: {type(data)}")
if isinstance(data, list):
    print(f"Count: {len(data)}")
    if len(data) > 0:
        print(f"First item: {list(data[0].keys())}")
elif isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  {k} has {len(v)} items")
            if len(v) > 0:
                print(f"    First item: {list(v[0].keys())}")
