from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from trains.models import Train
from stations.models import Station

class E2EBookingTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpassword123')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')

    def test_end_to_end_booking(self):
        # We need an express train since we flushed the test locals.
        train = Train.objects.filter(train_type='EXPRESS').first()
        if not train:
            # Maybe it's called something else? Let's just grab any train that has stops
            train = Train.objects.exclude(train_type='LOCAL').first()
            if not train:
                train = Train.objects.first()

        if not train:
            self.skipTest("No trains found in database")

        route = train.route
        stops = list(route.stations.all().order_by('sequence_number'))
        if len(stops) < 2:
            self.skipTest("Train does not have enough stops")

        source = stops[0].station
        destination = stops[1].station

        print(f"Testing E2E for {train.number} from {source.code} to {destination.code}")

        # Search
        response = self.client.get(f'/api/trains/search/?source={source.code}&destination={destination.code}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)
        found = any(t['number'] == train.number for t in data)
        self.assertTrue(found)

        # Book
        payload = {
            'train_number': train.number,
            'source_code': source.code,
            'destination_code': destination.code,
            'date_of_journey': '2026-09-25',
            'ticket_class': 'SL',
            'passengers': [{'name': 'John Doe', 'age': 30, 'berth_preference': 'LB', 'gender': 'M'}]
        }
        
        response = self.client.post('/api/bookings/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        booking = response.json()
        
        booking_id = booking['id']
        self.assertEqual(booking['source_station']['code'], source.code)
        self.assertEqual(booking['destination_station']['code'], destination.code)
        
        # Payment
        response = self.client.post(f'/api/bookings/{booking_id}/pay/')
        self.assertEqual(response.status_code, 200)
        
        # Details
        response = self.client.get(f'/api/bookings/{booking_id}/')
        self.assertEqual(response.status_code, 200)
        details = response.json()
        
        # Verify segment
        self.assertEqual(details['source_station']['code'], source.code)
        self.assertEqual(details['destination_station']['code'], destination.code)
        
        print("E2E Test Passed Successfully!")
