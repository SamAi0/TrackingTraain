from django import template
from accounts.models import User
from trains.models import Train
from stations.models import Station
from bookings.models import Booking
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def get_admin_stats():
    total_users = User.objects.count()
    total_trains = Train.objects.count()
    total_stations = Station.objects.count()
    total_bookings = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(status='CONFIRMED').count()
    cancelled_bookings = Booking.objects.filter(status='CANCELLED').count()
    total_revenue = Booking.objects.filter(status='CONFIRMED').aggregate(Sum('total_fare'))['total_fare__sum'] or 0
    
    return {
        'total_users': total_users,
        'total_trains': total_trains,
        'total_stations': total_stations,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue
    }
