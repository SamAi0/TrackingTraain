from django.urls import path
from .api_views import TrainSearchAPIView, RouteSearchAPIView

urlpatterns = [
    path('search/', RouteSearchAPIView.as_view(), name='api-route-search'),
    path('trains/', TrainSearchAPIView.as_view(), name='api-train-search'),
]
