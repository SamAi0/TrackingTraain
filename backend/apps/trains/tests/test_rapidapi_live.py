from django.test import TestCase
from rest_framework.test import APIClient
from django.conf import settings
from unittest.mock import patch

class RapidAPILiveIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_key = settings.RAPIDAPI_KEY

    def test_live_train_search_success(self):
        """Test train search hits RapidAPI directly and returns live data."""
        # Using a well-known train prefix '1295' (e.g. 12951 Mumbai Rajdhani)
        response = self.client.get('/api/trains/autocomplete/?q=1295')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        # We expect data to be returned from RapidAPI
        # We don't assert length because we don't control the external API, but it shouldn't be empty for '1295'
        if data:
            self.assertIn('number', data[0])
            self.assertIn('name', data[0])

    def test_live_station_trains_success(self):
        """Test live station hits RapidAPI directly and returns live data."""
        # 'NDLS' New Delhi is a busy station, should have trains
        response = self.client.get('/api/stations/NDLS/trains/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
        if data['results']:
            self.assertIn('train_number', data['results'][0])
            self.assertIn('arrival_time', data['results'][0])

    def test_live_invalid_api_key(self):
        """Test hitting RapidAPI with an invalid API key."""
        settings.RAPIDAPI_KEY = 'invalid_key_12345'
        response = self.client.get('/api/trains/autocomplete/?q=1295')
        
        self.assertIn(response.status_code, [401, 403])
        self.assertIn('error', response.json())
        
        # Restore valid key
        settings.RAPIDAPI_KEY = self.valid_key

    def test_missing_configuration(self):
        """Test behavior when API key configuration is completely missing."""
        settings.RAPIDAPI_KEY = ''
        response = self.client.get('/api/stations/NDLS/trains/')
        
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())
        
        # Restore valid key
        settings.RAPIDAPI_KEY = self.valid_key

    @patch('trains.services.rapidapi_service.requests.get')
    def test_429_rate_limit(self, mock_get):
        """Simulate a 429 Rate Limit from RapidAPI."""
        mock_response = mock_get.return_value
        mock_response.status_code = 429
        
        response = self.client.get('/api/trains/autocomplete/?q=1295')
        self.assertEqual(response.status_code, 429)
        self.assertIn('error', response.json())

    @patch('trains.services.rapidapi_service.requests.get')
    def test_502_bad_gateway(self, mock_get):
        """Simulate a 502 Bad Gateway from RapidAPI."""
        mock_response = mock_get.return_value
        mock_response.status_code = 502
        
        response = self.client.get('/api/trains/autocomplete/?q=1295')
        self.assertEqual(response.status_code, 502)
        self.assertIn('error', response.json())

    @patch('trains.services.rapidapi_service.requests.get')
    def test_504_timeout(self, mock_get):
        """Simulate a 504 Timeout from RapidAPI via exception."""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()
        
        response = self.client.get('/api/stations/NDLS/trains/')
        self.assertEqual(response.status_code, 504)
        self.assertIn('error', response.json())
