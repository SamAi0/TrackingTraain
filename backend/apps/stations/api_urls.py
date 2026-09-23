from django.urls import path
from .api_views import StationAutocompleteAPIView, StationListAPIView, StationGeoAPIView

urlpatterns = [
    path('autocomplete/', StationAutocompleteAPIView.as_view(), name='api-station-autocomplete'),
    path('list/', StationListAPIView.as_view(), name='api-station-list'),
    path('geo/', StationGeoAPIView.as_view(), name='api-station-geo'),
    # path('<str:code>/trains/', StationTrainsAPIView.as_view(), name='api-station-trains'),
]
