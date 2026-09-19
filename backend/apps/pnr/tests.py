from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import PNR
from bookings.models import Booking, Passenger
from django.contrib.auth import get_user_model
from trains.models import Train
from stations.models import Station
import datetime

User = get_user_model()

class PNRAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='booker', password='password123')
        self.station1 = Station.objects.create(code='NDLS', name='New Delhi', city='Delhi', state='Delhi')
        self.station2 = Station.objects.create(code='MMCT', name='Mumbai Central', city='Mumbai', state='MH')
        self.train = Train.objects.create(number='12951', name='Rajdhani Express', source=self.station1, destination=self.station2)
        
        self.booking = Booking.objects.create(
            user=self.user,
            train=self.train,
            source=self.station1,
            destination=self.station2,
            date_of_journey=datetime.date.today(),
            status='CONFIRMED',
            ticket_class='SL',
            total_fare=1500.00
        )
        
        Passenger.objects.create(
            booking=self.booking,
            name='John Doe',
            age=30,
            gender='M'
        )
        
        self.pnr = PNR.objects.create(
            booking=self.booking,
            status='CONFIRMED'
        )

    def test_valid_pnr_status(self):
        response = self.client.get(f'/api/pnr/{self.pnr.pnr_number}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming PNR API returns passengers directly or nested via booking
        self.assertTrue('pnr_number' in response.data)

    def test_invalid_pnr_status(self):
        response = self.client.get('/api/pnr/INVALID123/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
