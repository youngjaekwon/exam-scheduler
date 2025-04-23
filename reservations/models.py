from django.conf import settings
from django.db import models
from django.utils import timezone

from schedules.models import ExamSchedule


class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")
    schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="reservations")
    expected_participants = models.PositiveIntegerField()  # 예상 응시 인원 수
    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_confirmed"]),
        ]

    def _get_exam_schedule_for_update(self):
        """
        일정 객체를 select_for_update로 가져옵니다.

        - 동시성 제어를 위해 예약 확정/변경 시 반드시 사용해야 합니다.
        """
        return ExamSchedule.objects.select_for_update().get(id=self.schedule.id)

    def confirm(self):
        """
        예약을 확정 처리합니다.

        - 이미 확정된 예약은 예외 발생
        - 일정의 확정 인원을 증가시킵니다.
        """
        if self.is_confirmed:
            raise ValueError("예약이 이미 확정되었습니다.")

        schedule = self._get_exam_schedule_for_update()

        schedule.add_confirmed_participant(self.expected_participants)

        self.is_confirmed = True
        self.confirmed_at = timezone.now()
        self.save(update_fields=["is_confirmed", "confirmed_at"])

    def modify_participants(self, new_expected_participants):
        """
        확정된 예약의 인원 수를 변경합니다.

        - 확정되지 않은 예약은 변경 없이 무시됩니다.
        - 기존 인원을 제거한 뒤 새 인원 수로 반영합니다.
        """
        if not self.is_confirmed:
            return

        schedule = self._get_exam_schedule_for_update()

        schedule.remove_confirmed_participant(self.expected_participants)
        schedule.add_confirmed_participant(new_expected_participants)

    def cancel(self):
        """
        예약을 취소합니다.

        - 확정된 예약인 경우 확정 인원을 다시 감소시킵니다.
        - 예약 객체 자체의 삭제는 view에서 처리됩니다.
        """
        if not self.is_confirmed:
            return

        schedule = self._get_exam_schedule_for_update()

        schedule.remove_confirmed_participant(self.expected_participants)
