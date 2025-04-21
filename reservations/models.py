from django.conf import settings
from django.db import models
from django.utils import timezone

from schedules.models import ExamSchedule


class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")
    schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="reservations")
    expected_participants = models.PositiveIntegerField()
    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_confirmed"]),
        ]

    def _get_exam_schedule_for_update(self):
        return ExamSchedule.objects.select_for_update().get(id=self.schedule.id)

    def confirm(self):
        if self.is_confirmed:
            raise ValueError("예약이 이미 확정되었습니다.")

        schedule = self._get_exam_schedule_for_update()

        schedule.add_confirmed_participant(self.expected_participants)

        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=["is_confirmed", "confirmed_at"])

    def modify_participants(self, new_expected_participants):
        if not self.is_confirmed:
            return

        schedule = self._get_exam_schedule_for_update()

        schedule.remove_confirmed_participant(self.expected_participants)
        schedule.add_confirmed_participant(new_expected_participants)

    def cancel(self):
        if not self.is_confirmed:
            return

        schedule = self._get_exam_schedule_for_update()

        schedule.remove_confirmed_participant(self.expected_participants)
