from django.urls import path
from .api_views import BookingListCreateAPIView, BookingDetailAPIView, VerifyPaymentAPIView, ExpireBookingAPIView, CancelBookingAPIView
from .payment_views import ProcessPaymentAPIView
from . import payment_views

urlpatterns = [
    path('', BookingListCreateAPIView.as_view(), name='api-booking-list-create'),
    path('<int:pk>/', BookingDetailAPIView.as_view(), name='api-booking-detail'),
    path('<int:pk>/verify-payment/', VerifyPaymentAPIView.as_view(), name='api-booking-verify-payment'),
    path('<int:pk>/expire/', ExpireBookingAPIView.as_view(), name='api-booking-expire'),
    path('<int:pk>/cancel/', CancelBookingAPIView.as_view(), name='api-booking-cancel'),
    path('process-payment/', payment_views.ProcessPaymentAPIView.as_view(), name='process-payment'),
    path('payment-status/<int:payment_id>/', payment_views.CheckPaymentStatusAPIView.as_view(), name='payment-status'),
]
