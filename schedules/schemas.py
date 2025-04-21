from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status

from schedules.serializers import ExamScheduleSerializer

exam_schedule_create_schema = extend_schema(
    summary="시험 일정 생성",
    description="""시험 일정을 생성합니다.

    이 API는 관리자 권한이 필요합니다.
    """,
    request=ExamScheduleSerializer,
    responses={
        status.HTTP_201_CREATED: OpenApiResponse(
            response=ExamScheduleSerializer, description="시험 일정이 성공적으로 생성되었습니다."
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="유효하지 않은 입력 데이터입니다."),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없습니다."),
    },
)

exam_schedule_list_schema = extend_schema(
    summary="시험 일정 목록 조회",
    description="시험 일정 목록을 조회합니다.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=ExamScheduleSerializer(many=True), description="시험 일정 목록"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없습니다."),
    },
    parameters=[
        OpenApiParameter(
            name="search",
            description="검색어 (제목)",
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="start_time",
            description="시작 시간 (ISO 8601 형식, 예: 2025-04-21T23:00:00+09:00)",
            required=False,
            type=OpenApiTypes.DATETIME,
        ),
        OpenApiParameter(
            name="end_time",
            description="종료 시간 (ISO 8601 형식, 예: 2025-04-21T23:00:00+09:00)",
            required=False,
            type=OpenApiTypes.DATETIME,
        ),
        OpenApiParameter(
            name="ordering",
            description="정렬 기준 (제목, 시작 시간)",
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="page",
            description="페이지 번호",
            required=False,
            type=OpenApiTypes.INT,
        ),
    ],
)

exam_schedule_detail_schema = extend_schema(
    summary="시험 일정 상세 조회",
    description="시험 일정의 상세 정보를 조회합니다.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=ExamScheduleSerializer, description="시험 일정 상세 정보"),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없습니다."),
    },
)

exam_schedule_update_schema = extend_schema(
    summary="시험 일정 수정",
    description="""시험 일정을 수정합니다.

    이 API는 관리자 권한이 필요합니다.
    """,
    request=ExamScheduleSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=ExamScheduleSerializer, description="시험 일정이 성공적으로 수정되었습니다."
        ),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="유효하지 않은 입력 데이터입니다."),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없습니다."),
    },
)

exam_schedule_delete_schema = extend_schema(
    summary="시험 일정 삭제",
    description="""시험 일정을 삭제합니다.

    이 API는 관리자 권한이 필요합니다.
    """,
    responses={
        status.HTTP_204_NO_CONTENT: OpenApiResponse(description="시험 일정이 성공적으로 삭제되었습니다."),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="인증되지 않은 요청입니다."),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(description="권한이 없습니다."),
    },
)

exam_schedule_schema_view = extend_schema_view(
    list=exam_schedule_list_schema,
    create=exam_schedule_create_schema,
    retrieve=exam_schedule_detail_schema,
    update=exam_schedule_update_schema,
    partial_update=exam_schedule_update_schema,
    destroy=exam_schedule_delete_schema,
)
