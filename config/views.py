from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView


class HealthView(APIView):
    """Used by load balancers / Docker to check the app and database are alive."""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = []

    @extend_schema(responses={200: dict})
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return Response({"status": "ok"})


from users.serializers import CustomTokenObtainPairSerializer

class ThrottledTokenView(TokenObtainPairView):
    """Login endpoint with a stricter rate limit to slow down password guessing."""
    throttle_scope = "auth"
    serializer_class = CustomTokenObtainPairSerializer
