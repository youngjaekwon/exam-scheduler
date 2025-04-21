from django.contrib.auth import get_user_model
from rest_framework import serializers

from reservations.models import Reservation
from schedules.models import ExamSchedule

User = get_user_model()


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    schedule = serializers.PrimaryKeyRelatedField(queryset=ExamSchedule.objects.all())

    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = ["id", "user", "is_confirmed", "confirmed_at", "created_at"]
