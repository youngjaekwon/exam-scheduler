from django.conf import settings
from rest_framework import serializers

from schedules.models import ExamSchedule


class ExamScheduleSerializer(serializers.ModelSerializer):
    max_total_participants = serializers.SerializerMethodField()

    class Meta:
        model = ExamSchedule
        fields = "__all__"
        read_only_fields = ["id", "confirmed_participants"]

    def get_max_total_participants(self, obj):
        return settings.EXAM_SCHEDULE_MAX_PARTICIPANTS
