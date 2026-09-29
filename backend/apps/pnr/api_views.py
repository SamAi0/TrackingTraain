from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from .models import PNR
from .serializers import PNRSerializer

class PNRAnonRateThrottle(AnonRateThrottle):
    rate = '20/min'

class PNRStatusAPIView(APIView):
    throttle_classes = [PNRAnonRateThrottle]
    def get(self, request, pnr_number):
        from railway_api.services.pnr_service import PNRService
        result = PNRService.get_pnr(pnr_number)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND)
