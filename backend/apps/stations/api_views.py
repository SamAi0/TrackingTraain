from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Station

class StationAutocompleteAPIView(APIView):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        
        data = []
        if not q:
            return Response(data, status=status.HTTP_200_OK)
            
        # Fast local DB search
        stations = Station.objects.filter(
            Q(code__icontains=q) | 
            Q(name__icontains=q)
        ).order_by('name')[:10]
        
        for st in stations:
            data.append({
                'code': st.code,
                'name': st.name,
                'state': st.state,
                'latitude': st.latitude,
                'longitude': st.longitude
            })
            
        return Response(data, status=status.HTTP_200_OK)
