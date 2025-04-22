from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from schedules.models import ExamSchedule

User = get_user_model()

"""
예약 생성
- 정상 예약 - 성공
- 예약 마감 기간을 넘은 경우 - 실패
- 예약 인원을 초과한 경우 - 실패
- 로그인 하지 않은 사용자가 접근 - 실패
"""


class ReservationCreateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.schedule = ExamSchedule.objects.create(
            title="Test Exam",
            start_time=timezone.now() + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 1),
            end_time=timezone.now() + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 1, hours=2),
        )
        self.url = reverse("reservations:reservations-list")

    def test_create_reservation__success(self):
        # Given
        self.client.force_authenticate(user=self.user)
        payload = {
            "schedule_id": self.schedule.id,
            "expected_participants": 10,
        }

        # When
        response = self.client.post(self.url, payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("user", {}).get("id"), self.user.id)

    def test_create_reservation__fail_with_after_deadline(self):
        # Given
        self.client.force_authenticate(user=self.user)
        self.schedule.start_time = timezone.now() - timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 1)
        self.schedule.end_time = timezone.now() - timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 1, hours=2)
        self.schedule.save()
        payload = {
            "schedule_id": self.schedule.id,
            "expected_participants": 10,
        }

        # When
        response = self.client.post(self.url, payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation__fail_with_over_capacity(self):
        # Given
        self.client.force_authenticate(user=self.user)
        self.schedule.confirmed_participants = settings.EXAM_SCHEDULE_MAX_PARTICIPANTS
        self.schedule.save()
        payload = {
            "schedule_id": self.schedule.id,
            "expected_participants": 10,
        }

        # When
        response = self.client.post(self.url, payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation__fail_with_invalid_schedule(self):
        # Given
        self.client.force_authenticate(user=self.user)
        payload = {
            "schedule_id": 9999,  # Non-existent schedule ID
            "expected_participants": 10,
        }

        # When
        response = self.client.post(self.url, payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation__fail_with_unauthenticated_user(self):
        # Given
        payload = {
            "schedule_id": self.schedule.id,
            "expected_participants": 10,
        }

        # When
        response = self.client.post(self.url, payload, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
