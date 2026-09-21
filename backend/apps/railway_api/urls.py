from django.urls import path
from .views import (
    StationSearchAPIView,
    TrainSearchAPIView,
    TrainsBetweenAPIView,
    TrainScheduleV2APIView,
    TrainScheduleAPIView,
    LiveTrackingAPIView,
    PNRStatusAPIView,
    TrainClassesAPIView,
    SeatAvailabilityAPIView,
    SeatAvailabilityV2APIView,
    FareAPIView,
    StationTrainsAPIView,
    LiveStationAPIView
)

urlpatterns = [
    path('stations/search/', StationSearchAPIView.as_view(), name='railway-station-search'),
    path('trains/search-autocomplete/', TrainSearchAPIView.as_view(), name='railway-train-search'),
    path('trains/between/', TrainsBetweenAPIView.as_view(), name='railway-trains-between'),
    path('trains/<str:train_no>/schedule-v2/', TrainScheduleV2APIView.as_view(), name='railway-schedule-v2'),
    path('trains/<str:train_no>/schedule/', TrainScheduleAPIView.as_view(), name='railway-schedule'),
    path('trains/<str:train_no>/live/', LiveTrackingAPIView.as_view(), name='railway-live-tracking'),
    path('pnr/<str:pnr>/', PNRStatusAPIView.as_view(), name='railway-pnr'),
    path('trains/<str:train_no>/classes/', TrainClassesAPIView.as_view(), name='railway-train-classes'),
    path('trains/<str:train_no>/availability/', SeatAvailabilityAPIView.as_view(), name='railway-availability'),
    path('trains/<str:train_no>/availability-v2/', SeatAvailabilityV2APIView.as_view(), name='railway-availability-v2'),
    path('fare/', FareAPIView.as_view(), name='railway-fare'),
    path('stations/<str:code>/trains/', StationTrainsAPIView.as_view(), name='railway-station-trains'),
    path('stations/<str:code>/live/', LiveStationAPIView.as_view(), name='railway-live-station'),
]
