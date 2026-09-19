from django.urls import path
from .api_views import PNRStatusAPIView

urlpatterns = [
    path('<str:pnr_number>/', PNRStatusAPIView.as_view(), name='api-pnr-status'),
]
