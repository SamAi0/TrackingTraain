import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from trains.models import Train

class LiveTrackingAPIView(APIView):
    def get(self, request, train_number):
        from railway_api.services.tracking_service import TrackingService
        demo_delay = int(request.GET.get('demo_delay', 0))
        
        result = TrackingService.get_live_status(train_number, demo_delay=demo_delay)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND)

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
