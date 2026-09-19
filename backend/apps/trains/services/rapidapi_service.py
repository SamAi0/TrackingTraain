import requests
import logging
from django.conf import settings
from stations.models import Station
from trains.models import Train

logger = logging.getLogger(__name__)

class RapidAPIService:
    def __init__(self):
        self.api_key = settings.RAPIDAPI_KEY
        self.host = settings.RAPIDAPI_HOST
        self.base_url = f"https://{self.host}"
        
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.host
        }

    def _make_request(self, endpoint, params=None):
        if not self.api_key:
            logger.error("RAPIDAPI_KEY is missing from configuration.")
            return {'error': 'External API configuration error.', 'status_code': 500}
            
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=5)
            
            if response.status_code == 429:
                logger.warning(f"RapidAPI Rate Limit Exceeded: {endpoint}")
                return {'error': 'Too many requests to external service. Please try again later.', 'status_code': 429}
                
            response.raise_for_status()
            
            data = response.json()
            if not data.get('status'):
                return {'error': data.get('message', 'External API returned failure.'), 'status_code': 400}
                
            return {'data': data.get('data', []), 'status_code': 200}
            
        except requests.exceptions.Timeout:
            logger.error(f"RapidAPI Timeout: {endpoint}")
            return {'error': 'External service timed out.', 'status_code': 504}
        except requests.exceptions.RequestException as e:
            logger.error(f"RapidAPI RequestException: {endpoint} - {str(e)}")
            return {'error': 'External service is currently unavailable.', 'status_code': 502}
        except ValueError:
            logger.error(f"RapidAPI JSON Decode Error: {endpoint}")
            return {'error': 'Received invalid response from external service.', 'status_code': 502}

    def _map_station(self, code, name):
        """Attempts to find the station locally, otherwise returns a safe external representation."""
        try:
            station = Station.objects.get(code=code.upper())
            return {
                'code': station.code,
                'name': station.name,
                'city': station.city,
                'state': station.state,
                'is_external': False
            }
        except Station.DoesNotExist:
            return {
                'code': code.upper(),
                'name': name,
                'is_external': True
            }

    def _get_local_train_type(self, train_number):
        """Returns the local train type if the train exists, otherwise UNKNOWN."""
        try:
            train = Train.objects.get(number=train_number)
            return train.train_type
        except Train.DoesNotExist:
            return "UNKNOWN"

    def search_train(self, query):
        """Calls GET /api/v1/searchTrain and maps the response safely."""
        result = self._make_request('/api/v1/searchTrain', params={'query': query})
        if 'error' in result:
            return result
            
        mapped_data = []
        for item in result.get('data', []):
            train_number = item.get('train_number')
            mapped_data.append({
                'number': train_number,
                'name': item.get('train_name') or item.get('eng_train_name'),
                'train_type': self._get_local_train_type(train_number),
                'source': self._map_station(item.get('src_stn_code'), item.get('src_stn_name')),
                'destination': self._map_station(item.get('dstn_stn_code'), item.get('dstn_stn_name')),
                'is_external': True
            })
            
        return {'data': mapped_data, 'status_code': 200}

    def get_live_station(self, from_stn_code, to_stn_code=None, hours='1'):
        """Calls GET /api/v3/getLiveStation to get upcoming trains."""
        params = {
            'fromStationCode': from_stn_code,
            'hours': hours
        }
        if to_stn_code:
            params['toStationCode'] = to_stn_code
            
        result = self._make_request('/api/v3/getLiveStation', params=params)
        if 'error' in result:
            return result
            
        mapped_data = []
        for item in result.get('data', []):
            mapped_data.append({
                'number': item.get('trainNumber'),
                'name': item.get('trainName'),
                'train_type': item.get('trainType'),
                'schedule': {
                    'arrival_time': item.get('arrivalTime'),
                    'departure_time': item.get('departureTime'),
                },
                'run_days': item.get('runDays', {}),
                'classes': [c.get('value') for c in item.get('classes', [])],
                'is_external': True
            })
            
        return {'data': mapped_data, 'status_code': 200}
