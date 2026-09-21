from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    
    def perform_create(self, serializer):
        user = serializer.save()
        from utils.supabase_logger import SupabaseLogger
        SupabaseLogger.log_activity(
            user_id=user.id,
            activity_type='User Registration',
            metadata={'username': user.username}
        )

from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Login successful
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                from utils.supabase_logger import SupabaseLogger
                SupabaseLogger.log_activity(
                    user_id=user.id,
                    activity_type='User Login'
                )
            except User.DoesNotExist:
                pass
        return response
