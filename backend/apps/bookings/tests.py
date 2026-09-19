from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from trains.models import Train
from stations.models import Station
from .models import FareRule
import datetime

User = get_user_model()

class BookingAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='booker', password='password123')
        
        self.station1 = Station.objects.create(code='NDLS', name='New Delhi', city='Delhi', state='Delhi')
        self.station2 = Station.objects.create(code='MMCT', name='Mumbai Central', city='Mumbai', state='MH')
        self.train = Train.objects.create(number='12951', name='Rajdhani Express', source=self.station1, destination=self.station2, train_type='EXPRESS')
        
        FareRule.objects.create(
            train_type='EXPRESS',
            ticket_class='SL',
            base_fare=100.00,
            per_km_rate=1.50
        )

    def test_booking_unauthenticated(self):
        payload = {
            'train_number': '12951',
            'source_code': 'NDLS',
            'destination_code': 'MMCT',
            'ticket_class': 'SL',
            'passengers': [
                {'name': 'Jane Doe', 'age': 25, 'gender': 'F', 'berth_preference': 'L'}
            ],
            'date_of_journey': str(datetime.date.today())
        }
        response = self.client.post('/api/bookings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_booking_authenticated(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'train_number': '12951',
            'source_code': 'NDLS',
            'destination_code': 'MMCT',
            'ticket_class': 'SL',
            'passengers': [
                {'name': 'Jane Doe', 'age': 25, 'gender': 'F', 'berth_preference': 'L'}
            ],
            'date_of_journey': str(datetime.date.today())
        }
        response = self.client.post('/api/bookings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(len(response.data['passengers']), 1)
        self.assertEqual(response.data['passengers'][0]['name'], 'Jane Doe')
