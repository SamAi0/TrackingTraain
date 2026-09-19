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
        try:
            pnr = PNR.objects.get(pnr_number=pnr_number)
            serializer = PNRSerializer(pnr)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PNR.DoesNotExist:
            return Response({'error': 'Invalid PNR Number'}, status=status.HTTP_404_NOT_FOUND)
