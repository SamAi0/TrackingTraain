from django.urls import path
from .api_views import LiveTrackingAPIView, FrontendActivityAPIView

urlpatterns = [
    path('activity/', FrontendActivityAPIView.as_view(), name='api-frontend-activity'),
    path('<str:train_number>/', LiveTrackingAPIView.as_view(), name='api-live-tracking'),
]
