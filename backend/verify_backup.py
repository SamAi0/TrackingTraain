import os
import json

file_path = r"c:\Users\Asus\Desktop\Personal\rgc lcg\old_railway_backup.json"
size = os.path.getsize(file_path)

counts = {}
total_records = 0
try:
    with open(file_path, "rt", encoding="utf-16") as f:
        data = json.load(f)
        for obj in data:
            model = obj.get('model')
            counts[model] = counts.get(model, 0) + 1
            total_records += 1
    readability = "PASS"
except Exception as e:
    print(f"Error reading JSON: {e}")
    readability = "FAIL"

print("--- Backup Verification ---")
print(f"File size: {size / (1024*1024):.2f} MB")
print(f"Total Records: {total_records}")
print(f"Readability: {readability}")
print("\nTable-wise counts:")
for k, v in counts.items():
    print(f"{k}: {v}")
