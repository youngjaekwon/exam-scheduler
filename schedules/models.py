from datetime import timedelta

from django.conf import settings
from django.db import models


class ExamSchedule(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    confirmed_participants = models.PositiveIntegerField(default=0)  # 확정된 응시 인원 수

    class Meta:
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["start_time", "end_time"]),
        ]

    def add_confirmed_participant(self, participant_count):
        """
        확정된 응시 인원을 추가합니다.

        - 최대 인원(EXAM_SCHEDULE_MAX_PARTICIPANTS)을 초과하면 예외 발생
        """
        if self.confirmed_participants + participant_count > settings.EXAM_SCHEDULE_MAX_PARTICIPANTS:
            raise ValueError("최대 참가자 수를 초과하였습니다.")

        self.confirmed_participants += participant_count

        self.save(update_fields=["confirmed_participants"])

    def remove_confirmed_participant(self, participant_count):
        """
        확정된 응시 인원을 감소시킵니다.

        - 현재 확정된 인원보다 많이 제거하려 하면 예외 발생
        """
        if participant_count > self.confirmed_participants:
            raise ValueError("확정된 참가자 수보다 더 많은 참가자를 취소할 수 없습니다.")

        self.confirmed_participants -= participant_count

        self.save(update_fields=["confirmed_participants"])

    def get_reservation_deadline(self):
        """
        시험 예약 마감 시간을 반환합니다.

        - 시험 시작일 기준, 설정된 일 수(EXAM_RESERVATION_DEADLINE_DAYS) 이전
        """
        return self.start_time - timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS)

    def get_remaining_capacity(self):
        """
        현재 확정된 인원을 기준으로 남은 신청 가능 인원 수를 반환합니다.

        - 최대 허용 인원에서 확정된 인원을 뺀 값
        """
        return settings.EXAM_SCHEDULE_MAX_PARTICIPANTS - self.confirmed_participants
