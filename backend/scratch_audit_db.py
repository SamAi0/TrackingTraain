import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from stations.models import Station
from trains.models import Train
from routes.models import RouteStation, Route
from schedules.models import Schedule
from accounts.models import User
from bookings.models import Booking, Passenger
from pnr.models import PNR

import pymysql

report = {}

# 1. PostgreSQL Counts
report['postgres'] = {
    'Station': Station.objects.count(),
    'Train': Train.objects.count(),
    'Route': Route.objects.count(),
    'RouteStation': RouteStation.objects.count(),
    'Schedule': Schedule.objects.count(),
    'User': User.objects.count(),
    'Booking': Booking.objects.count(),
    'Passenger': Passenger.objects.count(),
    'PNR': PNR.objects.count(),
    'FareRule': 0,
    'Train_12951': Train.objects.filter(number='12951').exists(),
    'Train_01101': Train.objects.filter(number='01101').exists()
}

# 2. MySQL Counts
mysql_report = {}
try:
    conn = pymysql.connect(host='127.0.0.1', user='root', password='Admin', db='trackease')
    cursor = conn.cursor()
    
    tables = ['stations_station', 'trains_train', 'routes_route', 'routes_routestation', 'schedules_schedule']
    for t in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            mysql_report[t] = cursor.fetchone()[0]
        except:
            mysql_report[t] = 0
            
    cursor.execute("SELECT COUNT(*) FROM trains_train WHERE number='12951'")
    mysql_report['Train_12951'] = cursor.fetchone()[0] > 0
    
    cursor.execute("SELECT COUNT(*) FROM trains_train WHERE number='01101'")
    mysql_report['Train_01101'] = cursor.fetchone()[0] > 0
            
    conn.close()
    mysql_report['status'] = 'Connected'
except Exception as e:
    mysql_report['status'] = str(e)
    
report['mysql'] = mysql_report

# 3. JSON Files
json_report = {}
stations_file = 'data/raildrishti/stations.json'
schedules_file = 'data/raildrishti/schedules.json'

if os.path.exists(stations_file):
    json_report['stations_size'] = os.path.getsize(stations_file)
    with open(stations_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        json_report['stations_count'] = len(data)
else:
    json_report['stations_size'] = 0
    
if os.path.exists(schedules_file):
    json_report['schedules_size'] = os.path.getsize(schedules_file)
    with open(schedules_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        json_report['schedules_count'] = len(data)
        
        trains = set([item['train_number'] for item in data])
        json_report['unique_trains'] = len(trains)
        
        t12951 = [i for i in data if i['train_number'] == '12951']
        json_report['train_12951'] = len(t12951)
        
        t01101 = [i for i in data if i['train_number'] == '01101']
        json_report['train_01101'] = len(t01101)
else:
    json_report['schedules_size'] = 0

report['json'] = json_report

print(json.dumps(report, indent=2))
