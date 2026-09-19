from django.contrib import admin
from django.urls import path, include, re_path
from django.http import FileResponse, Http404
import os
from django.conf import settings
import mimetypes

FRONTEND_DIR = os.path.join(settings.BASE_DIR.parent, 'frontend')

def frontend_serve(request, path):
    if not path or path == '':
        path = 'index.html'
    
    file_path = os.path.join(FRONTEND_DIR, path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Guess the content type based on the file extension
        content_type, encoding = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    else:
        raise Http404(f"Frontend file not found: {path}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.api_urls')),
    path('api/trains/', include('trains.api_urls')),
    path('api/stations/', include('stations.api_urls')),
    path('api/pnr/', include('pnr.api_urls')),
    path('api/tracking/', include('tracking.api_urls')),
    path('api/bookings/', include('bookings.api_urls')),
    path('api/routes/', include('routes.api_urls')),
    # Catch-all route to serve the decoupled frontend files
    re_path(r'^(?P<path>.*)$', frontend_serve),
]
