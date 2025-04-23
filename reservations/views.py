from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from reservations.models import Reservation
from reservations.permissions import IsAdminOrOwnerWithEditableCondition
from reservations.schemas import reservation_schema_view
from reservations.serializers import ReservationSerializer, ReservationUpdateSerializer


@reservation_schema_view
class ReservationViewSet(viewsets.ModelViewSet):
    """
    예약 뷰셋
    - 예약 생성, 조회, 수정, 삭제, 확정 기능을 제공
    """

    permission_classes = [IsAuthenticated, IsAdminOrOwnerWithEditableCondition]
    filterset_fields = ["schedule", "user", "is_confirmed"]
    ordering_fields = ["created_at", "expected_participants"]
    search_fields = ["schedule__title"]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ReservationUpdateSerializer
        return ReservationSerializer

    def get_queryset(self):
        qs = Reservation.objects
        if self.action in ["list", "retrieve"]:
            # user와 schedule을 미리 가져오기 위해 select_related 사용
            # 나머지 action에서는 모델 메소드 내부에서 schedule을 가져옴
            qs = qs.select_related("user", "schedule")

        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        if self.request.method not in SAFE_METHODS:
            # 데이터 경합 방지를 위해 update, delete 시 select_for_update 사용
            queryset = queryset.select_for_update()

        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        reservation = serializer.instance
        new_expected_participants = serializer.validated_data.get(
            "expected_participants", reservation.expected_participants
        )

        if reservation.expected_participants != new_expected_participants:
            try:
                reservation.modify_participants(new_expected_participants)
            except ValueError as e:
                raise serializers.ValidationError({"detail": str(e)}) from e

        super().perform_update(serializer)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_destroy(self, reservation):
        try:
            reservation.cancel()
            super().perform_destroy(reservation)
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)}) from e

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="confirm", permission_classes=[IsAdminUser])
    @transaction.atomic
    def confirm(self, request, pk=None):
        reservation = self.get_object()

        try:
            reservation.confirm()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)
