from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import sys
import os

# Add the parent directory to sys.path to easily import the services module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.railway_api import RailwayTrackingService

class LiveTrackingAPIView(APIView):
    def get(self, request, train_number):
        # 1. Call the new Proxy Service
        status_data = RailwayTrackingService.get_live_status(train_number)
        
        # 2. Check if the service returned an error (e.g. missing API key)
        if "error" in status_data:
            return Response(status_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        # 3. Return the normalized clean data to the frontend
        return Response(status_data, status=status.HTTP_200_OK)
