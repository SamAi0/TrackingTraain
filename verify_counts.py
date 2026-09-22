import os
import sys
import django

# Add backend to path
sys.path.insert(0, os.path.abspath('backend'))

# Setup MySQL Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
mysql_counts = {}
models_to_check = [m for m in apps.get_models() if 'django' not in str(m.__module__) and 'rest_framework' not in str(m.__module__)]

print("--- MySQL Counts ---")
for m in models_to_check:
    count = m.objects.count()
    mysql_counts[m.__name__] = count
    print(f"{m.__name__}: {count}")

# Setup Supabase Django
import importlib
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings_migration'
importlib.reload(django.conf)
# Need to reset apps registry and connections to reconnect properly
from django.db import connections
connections.close_all()
django.setup()

print("\n--- Supabase Counts ---")
supabase_counts = {}
for m in models_to_check:
    count = m.objects.using('default').count()
    supabase_counts[m.__name__] = count
    print(f"{m.__name__}: {count}")

