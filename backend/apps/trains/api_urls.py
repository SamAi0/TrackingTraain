from django.urls import path
from .api_views import TrainSearchAPIView, FullRouteAPIView, TrainAutocompleteAPIView
from .api_stats import DashboardStatsAPIView
from tracking.api_views import LiveTrackingAPIView

urlpatterns = [
    path('autocomplete/', TrainAutocompleteAPIView.as_view(), name='api-train-autocomplete'),
    path('search/', TrainSearchAPIView.as_view(), name='api-train-search'),
    path('<str:train_number>/route/', FullRouteAPIView.as_view(), name='api-train-route'),
    path('<str:train_number>/track/', LiveTrackingAPIView.as_view(), name='api-train-track'),
    path('stats/', DashboardStatsAPIView.as_view(), name='api-train-stats'),
]
