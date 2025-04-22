from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from reservations.models import Reservation
from schedules.models import ExamSchedule
from schedules.serializers import ExamScheduleSerializer
from users.serializers.users import UserMeSerializer

User = get_user_model()


class ReservationSerializer(serializers.ModelSerializer):
    user = UserMeSerializer(read_only=True)
    schedule_id = serializers.PrimaryKeyRelatedField(
        queryset=ExamSchedule.objects.all(), source="schedule", write_only=True
    )
    schedule = ExamScheduleSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = ["id", "user", "is_confirmed", "confirmed_at", "created_at"]

    def validate(self, attrs):
        schedule = attrs.get("schedule")
        if timezone.now() > schedule.get_reservation_deadline():
            raise serializers.ValidationError("예약 마감 시간이 지났습니다.")
        expected_participants = attrs.get("expected_participants")
        if expected_participants > schedule.get_remaining_capacity():
            raise serializers.ValidationError("예약 가능한 인원 수를 초과했습니다.")
        return attrs


class ReservationUpdateSerializer(serializers.ModelSerializer):
    user = UserMeSerializer(read_only=True)
    schedule = ExamScheduleSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = ["id", "user", "schedule", "is_confirmed", "confirmed_at", "created_at"]

    def validate_expected_participants(self, value):
        instance = self.instance

        remaining_capacity = instance.schedule.get_remaining_capacity()

        allowed = (
            remaining_capacity + instance.expected_participants
            if instance and instance.is_confirmed
            else remaining_capacity
        )
        if value > allowed:
            raise serializers.ValidationError("예약 가능한 인원 수를 초과했습니다.")

        return value
