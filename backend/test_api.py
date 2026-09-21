from django.test import TestCase, Client
from django.urls import reverse

class TrainSearchAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.base_url = '/api/railway/trains/between/'

    def test_search_csmt_pnvl(self):
        """Test 1: CSMT to PNVL"""
        response = self.client.get(f'{self.base_url}?from=CSMT&to=PNVL')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('success', data)

    def test_search_pnvl_csmt(self):
        """Test 2: PNVL to CSMT (Reverse direction)"""
        response = self.client.get(f'{self.base_url}?from=PNVL&to=CSMT')
        self.assertEqual(response.status_code, 200)

    def test_search_sunday(self):
        """Test 3: Sunday running day filter"""
        response = self.client.get(f'{self.base_url}?from=CSMT&to=PNVL&date=2026-09-20')
        self.assertEqual(response.status_code, 200)

    def test_search_monday(self):
        """Test 4: Monday running day filter"""
        response = self.client.get(f'{self.base_url}?from=CSMT&to=PNVL&date=2026-09-21')
        self.assertEqual(response.status_code, 200)

    def test_search_pnvl_tna(self):
        """Test 5: PNVL to TNA"""
        response = self.client.get(f'{self.base_url}?from=PNVL&to=TNA')
        self.assertEqual(response.status_code, 200)
