import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_mysql')
django.setup()

from django.apps import apps

print("Table | Current Rows | App Label | Model Name")
print("-" * 60)
for model in apps.get_models():
    try:
        count = model.objects.count()
        print(f"{model._meta.db_table} | {count} | {model._meta.app_label} | {model.__name__}")
    except Exception as e:
        print(f"{model._meta.db_table} | ERROR: {e} | {model._meta.app_label} | {model.__name__}")
