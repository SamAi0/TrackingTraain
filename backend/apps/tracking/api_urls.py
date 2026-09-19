from django.urls import path
from .api_views import LiveTrackingAPIView

urlpatterns = [
    path('<str:train_number>/', LiveTrackingAPIView.as_view(), name='api-live-tracking'),
]
