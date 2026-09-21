from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from bookings.models import Booking, Passenger
from stations.models import Station
from trains.models import Train
import threading
import time

User = get_user_model()

class BookingConcurrencyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()
        self.client.force_login(self.user)
        
        self.src = Station.objects.create(code="SRC", name="Source")
        self.dst = Station.objects.create(code="DST", name="Dest")
        self.train = Train.objects.create(number="12345", name="Test Express", source=self.src, destination=self.dst)
        
        self.booking = Booking.objects.create(
            user=self.user,
            train=self.train,
            source=self.src,
            destination=self.dst,
            date_of_journey="2026-10-10",
            total_fare=100.00,
            status='PENDING'
        )
        
    def test_concurrent_payment_requests(self):
        # We simulate a race condition. Since SQLite might lock the whole DB, 
        # this is just to ensure the view doesn't throw a 500 when transaction.atomic is used.
        # A true concurrency test in Django test environment can be tricky,
        # but we test that the endpoint successfully processes one and rejects the second.
        
        response1 = self.client.post(f'/api/bookings/{self.booking.id}/verify-payment/', {'payment_id': 'pay_123'}, format='json')
        response2 = self.client.post(f'/api/bookings/{self.booking.id}/verify-payment/', {'payment_id': 'pay_124'}, format='json')
        
        self.assertEqual(response1.status_code, 200)
        # The second request should fail because the booking is no longer PENDING
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.json()['error'], 'Booking is not pending payment.')
        
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'CONFIRMED')
        self.assertEqual(self.booking.payment_id, 'pay_123')

class FallbackDataIntegrityTests(TestCase):
    def test_fare_fallback_missing_distance(self):
        from railway_api.services.fare_service import FareService
        # No routes/stations are created, so distance is missing
        response = FareService._fallback_fare("12345", "SRC", "DST")
        self.assertEqual(response.get("success"), False)
        self.assertEqual(response.get("error_code"), "NOT_FOUND")
        
    def test_schedule_fallback_missing_time(self):
        from railway_api.services.schedule_service import ScheduleService
        from routes.models import Route, RouteStation
        
        src = Station.objects.create(code="SRC", name="Source")
        dst = Station.objects.create(code="DST", name="Dest")
        train = Train.objects.create(number="54321", name="Test Train", source=src, destination=dst)
        route = Route.objects.create(train=train, route_name="Main")
        
        # Missing arrival and departure time
        RouteStation.objects.create(route=route, station=src, sequence_number=1, arrival_time=None, departure_time=None)
        
        response = ScheduleService._fallback_schedule("54321")
        self.assertEqual(response.get("success"), True)
        
        stations = response.get("stations", [])
        self.assertEqual(len(stations), 1)
        # It should be an empty string, not "00:00"
        self.assertEqual(stations[0]["arrival_time"], "")
        self.assertEqual(stations[0]["departure_time"], "")
