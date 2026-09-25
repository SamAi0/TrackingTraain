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
        from ..models import RapidAPIHistory
        from django.utils import timezone
        from datetime import timedelta
        
        # Allow passing full path (e.g. /api/v1/searchStation) or just the endpoint
        if endpoint.startswith('/'):
            url = f"{cls.get_base_url()}{endpoint}"
        else:
            url = f"{cls.get_base_url()}/api/v3/{endpoint}"

        # 1. Determine search identifier and filter matching records
        # To avoid date issues, we should ignore date-related params when caching if specified by user,
        # but the prompt says: "Do NOT use journey date as part of this matching logic for now."
        # We can make a copy of params without date keys
        cache_params = dict(params) if params else {}
        if 'dateOfJourney' in cache_params:
            del cache_params['dateOfJourney']
        if 'date' in cache_params:
            del cache_params['date']

        # Get latest successful matching response
        latest_history = RapidAPIHistory.objects.filter(
            endpoint=endpoint,
            request_params=cache_params,
            success=True
        ).order_by('-timestamp').first()

        # 2. Check if valid cache exists (within 3 months)
        if latest_history:
            three_months_ago = timezone.now() - timedelta(days=90)
            if latest_history.timestamp >= three_months_ago:
                # Valid cache found, return directly without calling RapidAPI
                return latest_history.response_json
                
        # 3. Call RapidAPI
        try:
            response = requests.get(
                url, 
                headers=cls.get_headers(), 
                params=params, 
                timeout=10
            )
            
            # Save history for successful requests
            if response.status_code == 200:
                try:
                    train_no = params.get('trainNo') or params.get('search') or params.get('pnrNumber') if params else None
                    res_json = response.json()
                    
                    # Store only if it's actually valid JSON and successful
                    RapidAPIHistory.objects.create(
                        endpoint=endpoint,
                        train_number=train_no,
                        request_params=cache_params,
                        http_status=response.status_code,
                        success=True,
                        response_json=res_json
                    )
                except Exception as e:
                    logger.error(f"Failed to save API history: {str(e)}")

            if response.status_code == 429:
                raise RailwayAPIException("Rate limit exceeded", "RATE_LIMITED", 429)
            elif response.status_code in [401, 403]:
                raise RailwayAPIException("Unauthorized external API access", "UNAUTHORIZED", response.status_code)
            elif response.status_code >= 500:
                raise RailwayAPIException("External railway service error", "EXTERNAL_SERVICE_ERROR", response.status_code)
                
            response.raise_for_status()
            return response.json()
            
        except (requests.exceptions.RequestException, RailwayAPIException) as e:
            # 4. Fallback: if API fails (quota exhausted, error, etc), use older cache if available
            if latest_history:
                logger.warning(f"RapidAPI failed ({str(e)}). Falling back to expired cached data.")
                return latest_history.response_json
            
            # If no cache exists, raise the error properly
            if isinstance(e, RailwayAPIException):
                raise e
            elif isinstance(e, requests.exceptions.Timeout):
                logger.error(f"Timeout connecting to {url}")
                raise RailwayAPIException("External API timeout", "TIMEOUT", 504)
            else:
                logger.error(f"Request failed: {str(e)}")
                raise RailwayAPIException(f"Failed to connect: {str(e)}", "CONNECTION_ERROR", 503)

    @classmethod
    def get_history(cls):
        from ..models import RapidAPIHistory
        # Returns history from local database
        return list(RapidAPIHistory.objects.all().order_by('-timestamp').values())
