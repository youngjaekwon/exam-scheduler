from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from users.serializers.users import UserRegisterSerializer, UserUpdateSerializer, UserMeSerializer
from users.schemas import user_register_schema, user_me_schema, user_me_update_schema

User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    """
    사용자 등록 뷰
    """

    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    @user_register_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserMeView(generics.RetrieveUpdateAPIView):
    """
    현재 사용자 정보 조회 및 수정 뷰
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserMeSerializer

    @user_me_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @user_me_update_schema
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @user_me_update_schema
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
