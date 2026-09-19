from django.core.management.base import BaseCommand
from trains.api_stats import DashboardStatsAPIView
from django.test import RequestFactory

class Command(BaseCommand):
    help = 'Warms up the dashboard stats cache by computing it natively.'

    def handle(self, *args, **options):
        self.stdout.write("Warming up stats cache...")
        request = RequestFactory().get('/api/trains/stats/')
        view = DashboardStatsAPIView()
        
        # We don't need to return the response, just run the view's get method
        # It will internally hit the `if not stats:` logic and cache.set() it.
        view.get(request)
        
        self.stdout.write(self.style.SUCCESS("Cache warmed successfully!"))
