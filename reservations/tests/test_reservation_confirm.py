from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from reservations.models import Reservation
from schedules.models import ExamSchedule

User = get_user_model()

"""
예약 확정
- 어드민이 예약을 확정한 경우 - 성공
- 어드민이 예약을 확정한 경우 - 예약 인원을 초과한 경우 - 실패
- 어드민이 예약을 확정한 경우 - 이미 확정된 예약인 경우 - 실패
- 유저가 예약 확정 시도를 한 경우 - 실패
- 로그인 하지 않은 사용자가 접근 - 실패
"""


class ReservationDeleteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.admin = User.objects.create_user(username="adminuser", password="adminpassword", is_staff=True)
        self.schedule = ExamSchedule.objects.create(
            title="Test Exam",
            start_time=timezone.now() + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 1),
            end_time=timezone.now() + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 1, hours=2),
        )
        self.reservation = Reservation.objects.create(
            user=self.user, schedule=self.schedule, expected_participants=5, is_confirmed=False
        )

    def get_url(self, pk):
        return reverse("reservations:reservations-confirm", args=[pk])

    def test_confirm_reservation__success(self):
        # Given
        self.client.force_authenticate(user=self.admin)
        url = self.get_url(self.reservation.id)

        # When
        response = self.client.post(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.is_confirmed)
        self.assertIsNotNone(self.reservation.confirmed_at)
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.confirmed_participants, 5)

    def test_confirm_reservation__fail_with_over_capacity(self):
        # Given
        self.client.force_authenticate(user=self.admin)
        url = self.get_url(self.reservation.id)
        self.schedule.confirmed_participants = settings.EXAM_SCHEDULE_MAX_PARTICIPANTS
        self.schedule.save()

        # When
        response = self.client.post(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.is_confirmed)
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.confirmed_participants, settings.EXAM_SCHEDULE_MAX_PARTICIPANTS)

    def test_confirm_reservation__fail_with_already_confirmed(self):
        # Given
        self.client.force_authenticate(user=self.admin)
        url = self.get_url(self.reservation.id)
        self.reservation.is_confirmed = True
        self.reservation.save()

        # When
        response = self.client.post(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.reservation.refresh_from_db()
        self.assertTrue(self.reservation.is_confirmed)

    def test_confirm_reservation__fail_with_non_admin_user(self):
        # Given
        self.client.force_authenticate(user=self.user)
        url = self.get_url(self.reservation.id)

        # When
        response = self.client.post(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.is_confirmed)

    def test_confirm_reservation__fail_with_unauthenticated_user(self):
        # Given
        url = self.get_url(self.reservation.id)

        # When
        response = self.client.post(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.reservation.refresh_from_db()
        self.assertFalse(self.reservation.is_confirmed)
