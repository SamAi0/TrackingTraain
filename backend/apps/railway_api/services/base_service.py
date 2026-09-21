import os
import requests
import logging
from django.conf import settings
from ..exceptions import RailwayAPIException

logger = logging.getLogger(__name__)

class BaseRailwayService:
    @classmethod
    def get_headers(cls):
        return {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": settings.RAPIDAPI_HOST
        }
    
    @classmethod
    def get_base_url(cls):
        return f"https://{settings.RAPIDAPI_HOST}"
    
    @classmethod
    def request(cls, endpoint, params=None):
        # Allow passing full path (e.g. /api/v1/searchStation) or just the endpoint
        if endpoint.startswith('/'):
            url = f"{cls.get_base_url()}{endpoint}"
        else:
            url = f"{cls.get_base_url()}/api/v3/{endpoint}"
            
        try:
            response = requests.get(
                url, 
                headers=cls.get_headers(), 
                params=params, 
                timeout=10
            )
            
            if response.status_code == 429:
                raise RailwayAPIException("Rate limit exceeded", "RATE_LIMITED", 429)
            elif response.status_code == 401 or response.status_code == 403:
                raise RailwayAPIException("Unauthorized external API access", "UNAUTHORIZED", response.status_code)
            elif response.status_code >= 500:
                raise RailwayAPIException("External railway service error", "EXTERNAL_SERVICE_ERROR", response.status_code)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout connecting to {url}")
            raise RailwayAPIException("External API timeout", "TIMEOUT", 504)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise RailwayAPIException(f"Failed to connect: {str(e)}", "CONNECTION_ERROR", 503)
