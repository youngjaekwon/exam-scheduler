from django.db import transaction
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from reservations.models import Reservation
from reservations.permissions import IsAdminOrOwnerWithEditableCondition
from reservations.schemas import reservation_schema_view
from reservations.serializers import ReservationSerializer


@reservation_schema_view
class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwnerWithEditableCondition]
    filterset_fields = ["schedule", "user", "is_confirmed"]
    ordering_fields = ["created_at", "expected_participants"]
    search_fields = ["schedule__title"]

    def get_queryset(self):
        qs = Reservation.objects.select_related("user", "schedule")
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(user=user)
        return qs.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        if self.request.method in SAFE_METHODS:
            obj = queryset.get(pk=self.kwargs["pk"])
        else:
            obj = queryset.select_for_update().get(pk=self.kwargs["pk"])

        self.check_object_permissions(self.request, obj)
        return obj

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.instance
        new_expected_participants = serializer.validated_data.get(
            "expected_participants", instance.expected_participants
        )

        if instance.expected_participants != new_expected_participants:
            try:
                instance.modify_participants(new_expected_participants)
            except ValueError as e:
                raise serializers.ValidationError({"detail": str(e)}) from e

        super().perform_update(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        try:
            instance.cancel()
            super().perform_destroy(instance)
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)}) from e

    @action(detail=True, methods=["post"], url_path="confirm", permission_classes=[IsAdminUser])
    @transaction.atomic
    def confirm(self, request, pk=None):
        reservation = self.get_object()

        try:
            reservation.confirm()
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})

        serializer = self.get_serializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)
