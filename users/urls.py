from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.views import UserRegisterView, UserMeView, JWTTokenObtainPairView, JWTTokenRefreshView

app_name = "users"

urlpatterns = [
    # 사용자 등록 API
    path("register/", UserRegisterView.as_view(), name="register"),
    # 현재 사용자 정보 조회/수정 API
    path("me/", UserMeView.as_view(), name="me"),
    # JWT 인증 API
    path("token/", JWTTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", JWTTokenRefreshView.as_view(), name="token_refresh"),
]
