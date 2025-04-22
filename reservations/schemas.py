from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status

from reservations.serializers import ReservationSerializer

reservation_create_schema = extend_schema(
    summary="예약 신청",
    description=(
        "시험 일정에 대한 예약을 신청합니다.\n\n"
        f"시험은 시험 시작 {settings.EXAM_RESERVATION_DEADLINE_DAYS}일 전까지 신청 가능합니다.\n\n"
        f"시험은 동 시간대에 최대 {settings.EXAM_SCHEDULE_MAX_PARTICIPANTS:,}명까지 신청 가능합니다."
    ),
    request=ReservationSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=ReservationSerializer, description="예약이 성공적으로 생성되었습니다."
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="유효하지 않은 입력 데이터입니다."),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
    },
)

reservation_list_schema = extend_schema(
    summary="예약 목록 조회",
    description="본인의 예약 목록을 조회합니다.\n\n관리자는 전체 예약 목록을 조회할 수 있습니다.\n\n",
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=ReservationSerializer(many=True), description="예약 목록"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
    },
    parameters=[
        OpenApiParameter(name="search", description="검색어 (시험 제목)", required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name="schedule", description="시험 일정 ID", required=False, type=OpenApiTypes.INT),
        OpenApiParameter(name="user", description="사용자 ID (관리자 전용)", required=False, type=OpenApiTypes.INT),
        OpenApiParameter(name="is_confirmed", description="확정 여부", required=False, type=OpenApiTypes.BOOL),
        OpenApiParameter(
            name="ordering", description="정렬 기준 (생성일, 응시 인원)", required=False, type=OpenApiTypes.STR
        ),
        OpenApiParameter(name="page", description="페이지 번호", required=False, type=OpenApiTypes.INT),
    ],
)

reservation_detail_schema = extend_schema(
    summary="예약 상세 조회",
    description="예약의 상세 정보를 조회합니다.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=ReservationSerializer, description="예약 상세 정보"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없습니다."),
    },
)

reservation_update_schema = extend_schema(
    summary="예약 수정",
    description="예약을 수정합니다.\n\n예약 수정은 확정 전 까지 가능합니다.\n\n관리자는 모든 예약을 수정할 수 있습니다.",
    request=ReservationSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=ReservationSerializer, description="예약이 수정되었습니다."),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="유효하지 않은 입력 데이터입니다."),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없습니다."),
    },
)

reservation_delete_schema = extend_schema(
    summary="예약 삭제",
    description="예약을 삭제합니다.\n\n예약 삭제는 확정 전 까지 가능합니다.\n\n관리자는 모든 예약을 삭제할 수 있습니다.",
    responses={
        status.HTTP_204_NO_CONTENT: OpenApiResponse(description="예약이 성공적으로 삭제되었습니다."),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없습니다."),
    },
)

reservation_confirm_schema = extend_schema(
    summary="예약 확정",
    description="""예약을 확정 처리합니다.
    
    이 API는 관리자 권한이 필요합니다.""",
    request=None,
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=ReservationSerializer, description="예약이 성공적으로 확정되었습니다."
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="유효하지 않은 요청입니다."),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없습니다."),
    },
)

reservation_schema_view = extend_schema_view(
    list=reservation_list_schema,
    create=reservation_create_schema,
    retrieve=reservation_detail_schema,
    update=reservation_update_schema,
    partial_update=reservation_update_schema,
    destroy=reservation_delete_schema,
    confirm=reservation_confirm_schema,
)
