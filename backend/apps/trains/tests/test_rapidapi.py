import unittest
from unittest.mock import patch, MagicMock
from trains.services.rapidapi_service import RapidAPIService
from stations.models import Station

class RapidAPIServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = RapidAPIService()
        
    @patch('trains.services.rapidapi_service.requests.get')
    @patch('trains.services.rapidapi_service.RapidAPIService._get_local_train_type')
    @patch('trains.services.rapidapi_service.RapidAPIService._map_station')
    def test_search_train_success(self, mock_map_station, mock_get_train_type, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': True,
            'data': [
                {
                    'train_number': '19038',
                    'train_name': 'Avadh Express',
                    'src_stn_code': 'BJU',
                    'src_stn_name': 'BARAUNI JN',
                    'dstn_stn_code': 'BDTS',
                    'dstn_stn_name': 'MUMBAI BANDRA TERMINUS'
                }
            ]
        }
        mock_get.return_value = mock_response
        mock_get_train_type.return_value = 'UNKNOWN'
        
        # Mock station mapping responses
        def side_effect_map_station(code, name):
            return {
                'code': code,
                'name': name,
                'is_external': True
            }
        mock_map_station.side_effect = side_effect_map_station
        
        result = self.service.search_train('190')
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(len(result['data']), 1)
        
        train_data = result['data'][0]
        self.assertEqual(train_data['number'], '19038')
        self.assertEqual(train_data['name'], 'Avadh Express')
        self.assertEqual(train_data['train_type'], 'UNKNOWN')
        self.assertTrue(train_data['is_external'])
        
        self.assertEqual(train_data['source']['code'], 'BJU')
        self.assertEqual(train_data['source']['name'], 'BARAUNI JN')
        self.assertTrue(train_data['source']['is_external'])

    @patch('trains.services.rapidapi_service.requests.get')
    def test_rate_limit(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        result = self.service.search_train('190')
        self.assertEqual(result['status_code'], 429)
        self.assertIn('error', result)
        self.assertIn('Too many requests', result['error'])

    @patch('trains.services.rapidapi_service.requests.get')
    def test_timeout(self, mock_get):
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout()
        result = self.service.search_train('190')
        self.assertEqual(result['status_code'], 504)
        
    @patch('trains.services.rapidapi_service.requests.get')
    def test_connection_error(self, mock_get):
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError()
        result = self.service.search_train('190')
        self.assertEqual(result['status_code'], 502)
        
    @patch('trains.services.rapidapi_service.requests.get')
    def test_invalid_json(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError()
        mock_get.return_value = mock_response
        result = self.service.search_train('190')
        self.assertEqual(result['status_code'], 502)
        
    def test_missing_api_key(self):
        self.service.api_key = ''
        result = self.service.search_train('190')
        self.assertEqual(result['status_code'], 500)
        
    @patch('trains.services.rapidapi_service.requests.get')
    def test_http_401(self, mock_get):
        from requests.exceptions import HTTPError
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = HTTPError()
        mock_get.return_value = mock_response
        result = self.service.search_train('190')
        self.assertEqual(result['status_code'], 502)

if __name__ == '__main__':
    unittest.main()
