from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import find_direct_trains, get_route_timeline, find_multi_train_route

class TrainSearchAPIView(APIView):
    def get(self, request):
        src_code = request.GET.get('from')
        dest_code = request.GET.get('to')
        
        if not src_code or not dest_code:
            return Response({"error": "Missing 'from' or 'to' parameters."}, status=status.HTTP_400_BAD_REQUEST)
            
        trains = find_direct_trains(src_code.upper(), dest_code.upper())
        return Response({"trains": trains}, status=status.HTTP_200_OK)


class RouteSearchAPIView(APIView):
    def get(self, request):
        src_code = request.GET.get('from')
        dest_code = request.GET.get('to')
        train_number = request.GET.get('train')
        
        if not src_code or not dest_code:
            return Response({"error": "Missing 'from' or 'to' parameters."}, status=status.HTTP_400_BAD_REQUEST)
            
        if not train_number:
            # If train not specified, find the first available direct train
            trains = find_direct_trains(src_code.upper(), dest_code.upper())
            if not trains:
                # Fallback to multi-train Dijkstra search
                multi_route = find_multi_train_route(src_code.upper(), dest_code.upper())
                if multi_route:
                    return Response(multi_route, status=status.HTTP_200_OK)
                return Response({"error": "No valid railway route found between these stations."}, status=status.HTTP_404_NOT_FOUND)
            train_number = trains[0]["train_number"]
            
        timeline = get_route_timeline(train_number, src_code.upper(), dest_code.upper())
        
        if not timeline:
            return Response({"error": "Could not generate timeline for the selected route."}, status=status.HTTP_404_NOT_FOUND)
            
        # Wrap single direct train in the same segment structure to unify frontend rendering if we want,
        # but the prompt says: "Direct Route Must Remain Preferred... The existing direct-train functionality is already working. Do not replace it unnecessarily."
        # We'll just return the original timeline structure.
        return Response(timeline, status=status.HTTP_200_OK)
