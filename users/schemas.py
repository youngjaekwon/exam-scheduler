from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status

from .serializers import UserRegisterSerializer


user_register_schema = extend_schema(
    summary="사용자 등록",
    description="새로운 사용자를 등록합니다. 사용자명, 이메일, 비밀번호가 필요합니다.",
    request=UserRegisterSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=UserRegisterSerializer,
            description="사용자가 성공적으로 등록되었습니다."
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description="유효하지 않은 입력 데이터입니다."
        ),
    },
)


user_me_schema = extend_schema(
    summary="현재 사용자 정보 조회",
    description="현재 로그인된 사용자의 정보를 조회합니다.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=UserRegisterSerializer(exclude=["password", "password_confirm"]),
            description="현재 로그인된 사용자 정보"
        ),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
            description="인증되지 않은 요청입니다."
        ),
    },
)


user_me_update_schema = extend_schema(
    summary="현재 사용자 정보 업데이트",
    description="현재 로그인된 사용자의 정보를 업데이트합니다.",
    request=UserRegisterSerializer(exclude=["password_confirm"]),
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=UserRegisterSerializer(exclude=["password", "password_confirm"]),
            description="업데이트된 사용자 정보"
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description="유효하지 않은 입력 데이터입니다."
        ),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
            description="인증되지 않은 요청입니다."
        ),
    },
) 