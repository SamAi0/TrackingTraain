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

class FrontendActivityAPIView(APIView):
    def post(self, request):
        from utils.supabase_logger import SupabaseLogger
        activity_type = request.data.get('activity_type')
        user_id = request.user.id if request.user.is_authenticated else None
        
        if not activity_type:
            return Response({'error': 'activity_type is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        SupabaseLogger.log_activity(
            user_id=user_id,
            activity_type=activity_type,
            from_station=request.data.get('from_station'),
            to_station=request.data.get('to_station'),
            train_number=request.data.get('train_number'),
            booking_id=request.data.get('booking_id'),
            pnr=request.data.get('pnr'),
            metadata=request.data.get('metadata')
        )
        return Response({'success': True}, status=status.HTTP_200_OK)
