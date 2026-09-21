import os
import json
import logging
import threading
import urllib.request
from urllib.error import URLError, HTTPError
from django.utils import timezone

logger = logging.getLogger(__name__)

class SupabaseLogger:
    @staticmethod
    def _send_log_async(payload):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            return
            
        endpoint = f"{supabase_url}/rest/v1/user_activity_logs"
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(endpoint, data=data, headers=headers, method='POST')
            
            # Short timeout to ensure it doesn't block background threads excessively
            with urllib.request.urlopen(req, timeout=3) as response:
                pass # Success
        except HTTPError as e:
            logger.warning(f"Supabase logging HTTP error: {e.code} - {e.reason}")
        except URLError as e:
            logger.warning(f"Supabase logging URL error: {e.reason}")
        except Exception as e:
            logger.warning(f"Supabase logging unexpected error: {str(e)}")

    @staticmethod
    def log_activity(user_id=None, activity_type=None, from_station=None, to_station=None, 
                     train_number=None, journey_date=None, booking_id=None, pnr=None, 
                     status=None, data_source=None, metadata=None):
        """
        Log user activity to Supabase asynchronously.
        Does not block the main application thread.
        """
        if not activity_type:
            return
            
        payload = {
            "activity_type": activity_type,
            "timestamp": timezone.now().isoformat()
        }
        
        if user_id: payload["user_id"] = user_id
        if from_station: payload["from_station"] = from_station
        if to_station: payload["to_station"] = to_station
        if train_number: payload["train_number"] = train_number
        if journey_date: payload["journey_date"] = journey_date
        if booking_id: payload["booking_id"] = booking_id
        if pnr: payload["pnr"] = pnr
        if status: payload["status"] = status
        if data_source: payload["data_source"] = data_source
        if metadata: payload["metadata"] = metadata
        
        try:
            # Create a short-lived daemon thread to send the log
            thread = threading.Thread(target=SupabaseLogger._send_log_async, args=(payload,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            logger.error(f"Failed to start Supabase logging thread: {str(e)}")
