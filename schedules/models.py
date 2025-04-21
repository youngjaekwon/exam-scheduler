from django.conf import settings
from django.db import models


class ExamSchedule(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    confirmed_participants = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["start_time", "end_time"]),
        ]

    def add_confirmed_participant(self, participant_count):
        if self.confirmed_participants + participant_count > settings.EXAM_SCHEDULE_MAX_PARTICIPANTS:
            raise ValueError("최대 참가자 수를 초과하였습니다.")

        self.confirmed_participants += participant_count

        self.save(update_fields=["confirmed_participants"])

    def remove_confirmed_participant(self, participant_count):
        if participant_count > self.confirmed_participants:
            raise ValueError("확정된 참가자 수보다 더 많은 참가자를 취소할 수 없습니다.")

        self.confirmed_participants -= participant_count

        self.save(update_fields=["confirmed_participants"])
