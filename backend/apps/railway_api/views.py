from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services.station_service import StationService
from .services.train_service import TrainService
from .services.schedule_service import ScheduleService

class StationSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        result = StationService.search_station(query)
        http_status = status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST
        if result.get('error_code') in ['UNAUTHORIZED', 'RATE_LIMITED', 'EXTERNAL_SERVICE_ERROR']:
            # We still return 200 with the fallback data if success is True
            # But if it completely failed and success is False:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE if result.get('error_code') != 'INVALID_REQUEST' else status.HTTP_400_BAD_REQUEST
        
        # In our normalizer, if fallback succeeds, success is True, so it returns 200 OK.
        return Response(result, status=status.HTTP_200_OK if result.get('success') else http_status)

class TrainSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        result = TrainService.search_train(query)
        if result.get('success'):
            from utils.supabase_logger import SupabaseLogger
            SupabaseLogger.log_activity(
                user_id=request.user.id if request.user.is_authenticated else None,
                activity_type='Train Search Autocomplete',
                metadata={'query': query}
            )
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)

class TrainsBetweenAPIView(APIView):
    def get(self, request):
        from_stn = request.query_params.get('from', '')
        to_stn = request.query_params.get('to', '')
        date = request.query_params.get('date', None)
        
        result = TrainService.trains_between(from_stn, to_stn, date)
        if result.get('success'):
            from utils.supabase_logger import SupabaseLogger
            SupabaseLogger.log_activity(
                user_id=request.user.id if request.user.is_authenticated else None,
                activity_type='Train Search',
                from_station=from_stn,
                to_station=to_stn,
                journey_date=date,
                data_source=result.get('source')
            )
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)

class TrainScheduleV2APIView(APIView):
    def get(self, request, train_no):
        result = ScheduleService.get_schedule(train_no, is_v2=True)
        if result.get('success'):
            from utils.supabase_logger import SupabaseLogger
            SupabaseLogger.log_activity(
                user_id=request.user.id if request.user.is_authenticated else None,
                activity_type='Train Details Viewed',
                train_number=train_no,
                data_source=result.get('source')
            )
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND)

class TrainScheduleAPIView(APIView):
    def get(self, request, train_no):
        result = ScheduleService.get_schedule(train_no, is_v2=False)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND)

from .services.tracking_service import TrackingService
from .services.pnr_service import PNRService
from .services.availability_service import AvailabilityService
from .services.fare_service import FareService

class LiveTrackingAPIView(APIView):
    def get(self, request, train_no):
        date = request.query_params.get('date', None)
        result = TrackingService.get_live_status(train_no, date)
        if result.get('success'):
            from utils.supabase_logger import SupabaseLogger
            SupabaseLogger.log_activity(
                user_id=request.user.id if request.user.is_authenticated else None,
                activity_type='Train Tracking',
                train_number=train_no,
                journey_date=date,
                data_source=result.get('source')
            )
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND)

class PNRStatusAPIView(APIView):
    def get(self, request, pnr):
        result = PNRService.get_pnr(pnr)
        if result.get('success'):
            from utils.supabase_logger import SupabaseLogger
            SupabaseLogger.log_activity(
                user_id=request.user.id if request.user.is_authenticated else None,
                activity_type='PNR Status Check',
                pnr=pnr,
                data_source=result.get('source')
            )
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND)

class TrainClassesAPIView(APIView):
    def get(self, request, train_no):
        result = TrainService.get_classes(train_no)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)

class SeatAvailabilityAPIView(APIView):
    def get(self, request, train_no):
        from_stn = request.query_params.get('from', '')
        to_stn = request.query_params.get('to', '')
        date = request.query_params.get('date', '')
        class_code = request.query_params.get('class', '')
        quota = request.query_params.get('quota', 'GN')
        
        result = AvailabilityService.check(train_no, from_stn, to_stn, date, class_code, quota, is_v2=False)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)

class SeatAvailabilityV2APIView(APIView):
    def get(self, request, train_no):
        from_stn = request.query_params.get('from', '')
        to_stn = request.query_params.get('to', '')
        date = request.query_params.get('date', '')
        class_code = request.query_params.get('class', '')
        quota = request.query_params.get('quota', 'GN')
        
        result = AvailabilityService.check(train_no, from_stn, to_stn, date, class_code, quota, is_v2=True)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)

class FareAPIView(APIView):
    def get(self, request):
        train_no = request.query_params.get('train_no', '')
        from_stn = request.query_params.get('from', '')
        to_stn = request.query_params.get('to', '')
        quota = request.query_params.get('quota', 'GN')
        
        result = FareService.get_fare(train_no, from_stn, to_stn, quota)
        if result.get('success'):
            from utils.supabase_logger import SupabaseLogger
            SupabaseLogger.log_activity(
                user_id=request.user.id if request.user.is_authenticated else None,
                activity_type='Fare Checked',
                train_number=train_no,
                from_station=from_stn,
                to_station=to_stn,
                metadata={'quota': quota},
                data_source=result.get('source')
            )
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)

class StationTrainsAPIView(APIView):
    def get(self, request, code):
        result = StationService.get_trains(code)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND)

class LiveStationAPIView(APIView):
    def get(self, request, code):
        result = StationService.get_live(code)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND)

