from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.serializers.jwt import CustomTokenObtainPairSerializer
from users.schemas import token_obtain_schema, token_refresh_schema


class JWTTokenObtainPairView(TokenObtainPairView):
    """
    JWT 토큰 발급 뷰
    """

    serializer_class = CustomTokenObtainPairSerializer

    @token_obtain_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class JWTTokenRefreshView(TokenRefreshView):
    """
    JWT 토큰 갱신 뷰
    """

    @token_refresh_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
