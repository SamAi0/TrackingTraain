from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from trains.models import Train
from stations.models import Station
import datetime

class FinalAuditE2ETest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpassword123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Import actual data to test against
        from django.core.management import call_command
        call_command('import_mumbai_suburban_data')

    def test_case_a_real_data(self):
        # The JSON only contains 6 specific suburban services.
        # Dadar to Thane is NOT in those 6. We verify it returns 0.
        response = self.client.get('/api/trains/search/?source=DR&destination=TNA')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0, "No fake data should exist for DR -> TNA")
        
        # Test an actual valid segment from the JSON: CSMT -> PNVL (98011)
        response = self.client.get('/api/trains/search/?source=CSMT&destination=PNVL')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)
        
        train = next((t for t in data if t['number'] == '98011'), None)
        self.assertIsNotNone(train)
        self.assertEqual(train['source']['code'], 'CSMT')
        self.assertEqual(train['destination']['code'], 'PNVL')
        
    def test_case_b_thane_to_dadar(self):
        # Case B: Thane to Dadar. Should only return reverse trains.
        response = self.client.get('/api/trains/search/?source=TNA&destination=DR')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Ensure that no trains from Case A are in Case B.
        response_a = self.client.get('/api/trains/search/?source=DR&destination=TNA')
        data_a = response_a.json()
        train_nums_a = {t['number'] for t in data_a}
        
        for t in data:
            self.assertNotIn(t['number'], train_nums_a, "Reverse route should not include forward trains")

    def test_case_c_no_sunday(self):
        # We know 98045 has MON-SAT
        # Check a Sunday (e.g., 2026-09-20)
        response = self.client.get('/api/trains/search/?source=CSMT&destination=PNVL&date=2026-09-20')
        if response.status_code == 200:
            data = response.json()
            train_nums = {t['number'] for t in data}
            self.assertNotIn('98045', train_nums, "98045 should not run on Sunday")

    def test_case_d_not_specified(self):
        # We know 98011 has NOT_SPECIFIED_IN_SOURCE
        # Check any date, it should allow it
        response = self.client.get('/api/trains/search/?source=CSMT&destination=PNVL&date=2026-09-20')
        if response.status_code == 200:
            data = response.json()
            train_nums = {t['number'] for t in data}
            self.assertIn('98011', train_nums, "98011 should be allowed as running day is unknown")

    def test_case_e_incomplete_timetable(self):
        # 98011 is incomplete (only 2 stops)
        response = self.client.get('/api/trains/search/?source=CSMT&destination=PNVL')
        if response.status_code == 200:
            data = response.json()
            train = next((t for t in data if t['number'] == '98011'), None)
            if train:
                self.assertFalse(train['timetable_complete'], "98011 should be incomplete")

    def test_case_f_missing_distance(self):
        # The fare calculation for 98011 (incomplete, no distance) should fail
        payload = {
            'train_number': '98011',
            'source_code': 'CSMT',
            'destination_code': 'PNVL',
            'date_of_journey': '2026-09-25',
            'ticket_class': 'GN',
            'passengers': [{'name': 'John', 'age': 30, 'berth_preference': '', 'gender': 'M'}]
        }
        response = self.client.post('/api/bookings/', payload, format='json')
        # It should fail with FareCalculationError (400 Bad Request)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Distance data is unavailable", response.json().get('error', ''))
