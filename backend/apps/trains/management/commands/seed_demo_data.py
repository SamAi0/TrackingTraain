from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from stations.models import Station
from trains.models import Train
from routes.models import Route, RouteStation
from pnr.models import PNR
from bookings.models import Booking
import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the MySQL database with realistic demo data for TrackEase'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing old demo data...')
        Booking.objects.all().delete()
        PNR.objects.all().delete()
        RouteStation.objects.all().delete()
        Route.objects.all().delete()
        Train.objects.all().delete()
        Station.objects.all().delete()

        self.stdout.write('Creating Stations...')
        
        # Define stations with Lat/Lng
        station_data = [
            {'code': 'MMCT', 'name': 'Mumbai Central', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 18.9696, 'lng': 72.8193},
            {'code': 'BVI', 'name': 'Borivali', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.2307, 'lng': 72.8567},
            {'code': 'ST', 'name': 'Surat', 'city': 'Surat', 'state': 'Gujarat', 'lat': 21.2049, 'lng': 72.8407},
            {'code': 'BRC', 'name': 'Vadodara Junction', 'city': 'Vadodara', 'state': 'Gujarat', 'lat': 22.3106, 'lng': 73.1800},
            {'code': 'RTM', 'name': 'Ratlam Junction', 'city': 'Ratlam', 'state': 'Madhya Pradesh', 'lat': 23.3323, 'lng': 75.0456},
            {'code': 'KOTA', 'name': 'Kota Junction', 'city': 'Kota', 'state': 'Rajasthan', 'lat': 25.1764, 'lng': 75.8340},
            {'code': 'NDLS', 'name': 'New Delhi', 'city': 'Delhi', 'state': 'Delhi', 'lat': 28.6429, 'lng': 77.2191},
            {'code': 'CSTM', 'name': 'Chhatrapati Shivaji Maharaj Terminus', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 18.9398, 'lng': 72.8354},
            {'code': 'DR', 'name': 'Dadar', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.0178, 'lng': 72.8437},
            {'code': 'KYN', 'name': 'Kalyan Junction', 'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.2354, 'lng': 73.1316},
            {'code': 'PUNE', 'name': 'Pune Junction', 'city': 'Pune', 'state': 'Maharashtra', 'lat': 18.5284, 'lng': 73.8738}
        ]
        
        stations = {}
        for s in station_data:
            stations[s['code']] = Station.objects.create(
                code=s['code'], name=s['name'], city=s['city'], state=s['state'],
                latitude=s['lat'], longitude=s['lng']
            )

        self.stdout.write('Creating Trains...')
        rajdhani = Train.objects.create(
            number='12951', name='Rajdhani Express', train_type='EXPRESS',
            source=stations['MMCT'], destination=stations['NDLS']
        )
        if 'CSTM' in stations and 'PUNE' in stations:
            deccan_queen, _ = Train.objects.get_or_create(
                number='12123',
                defaults={'name': 'Deccan Queen', 'train_type': 'SF', 
                          'source': stations['CSTM'], 'destination': stations['PUNE']}
            )

        self.stdout.write('Creating Routes...')
        rajdhani_route = Route.objects.create(train=rajdhani)
        
        RouteStation.objects.create(route=rajdhani_route, station=stations['MMCT'], sequence_number=1, distance_from_source=0)
        RouteStation.objects.create(route=rajdhani_route, station=stations['BVI'], sequence_number=2, distance_from_source=29)
        RouteStation.objects.create(route=rajdhani_route, station=stations['ST'], sequence_number=3, distance_from_source=263)
        RouteStation.objects.create(route=rajdhani_route, station=stations['BRC'], sequence_number=4, distance_from_source=393)
        RouteStation.objects.create(route=rajdhani_route, station=stations['RTM'], sequence_number=5, distance_from_source=654)
        RouteStation.objects.create(route=rajdhani_route, station=stations['KOTA'], sequence_number=6, distance_from_source=920)
        RouteStation.objects.create(route=rajdhani_route, station=stations['NDLS'], sequence_number=7, distance_from_source=1386)

        # Routes for Deccan Queen
        if 'CSTM' in stations and 'PUNE' in stations:
            deccan_route, _ = Route.objects.get_or_create(train=deccan_queen, defaults={'name': 'Mumbai-Pune Route'})
            RouteStation.objects.create(route=deccan_route, station=stations['CSTM'], sequence_number=1, distance_from_source=0)
            RouteStation.objects.create(route=deccan_route, station=stations['DR'], sequence_number=2, distance_from_source=9)
            RouteStation.objects.create(route=deccan_route, station=stations['KYN'], sequence_number=3, distance_from_source=51)
            RouteStation.objects.create(route=deccan_route, station=stations['PUNE'], sequence_number=4, distance_from_source=192)

        self.stdout.write('Creating Demo Bookings & PNRs...')
        demo_user, _ = User.objects.get_or_create(username='demouser', email='demo@trackease.com')
        if _:
            demo_user.set_password('demo123')
            demo_user.save()

        demo_pnr = PNR.objects.create(
            pnr_number='1234567890', train=rajdhani, passenger_name='Rahul Sharma', passenger_age=28,
            source=stations['MMCT'], destination=stations['NDLS'],
            date_of_journey=datetime.date.today() + datetime.timedelta(days=2), status='CONFIRMED', seat_number='B1-42'
        )

        Booking.objects.create(user=demo_user, pnr=demo_pnr, total_fare=2500.00)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with realistic demo data!'))
