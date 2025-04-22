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
예약 삭제
- 예약 확정 전 유저가 삭제한 경우 - 성공
- 예약 확정 후 유저가 삭제한 경우 - 실패
- 예약 확정 후 어드민이 삭제한 경우 - 성공 - schedule 의 confirmed_participants 수 감소 확인
- 다른 유저의 예약을 삭제 시도 하는 경우 - 실패
- 로그인 하지 않은 사용자가 접근 - 실패
"""


class ReservationDeleteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpassword")
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
        return reverse("reservations:reservations-detail", args=[pk])

    def test_delete_reservation__success(self):
        # Given
        self.client.force_authenticate(user=self.user)
        url = self.get_url(self.reservation.id)

        # When
        response = self.client.delete(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reservation.objects.filter(id=self.reservation.id).exists())
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.confirmed_participants, 0)

    def test_delete_reservation__fail_with_after_confirmation(self):
        # Given
        self.reservation.is_confirmed = True
        self.reservation.save()
        self.client.force_authenticate(user=self.user)
        url = self.get_url(self.reservation.id)

        # When
        response = self.client.delete(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())

    def test_delete_reservation__success_with_after_confirmation_and_admin_user(self):
        # Given
        self.reservation.is_confirmed = True
        self.reservation.save()
        self.schedule.confirmed_participants += self.reservation.expected_participants
        self.schedule.save()
        self.client.force_authenticate(user=self.admin)
        url = self.get_url(self.reservation.id)

        # When
        response = self.client.delete(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reservation.objects.filter(id=self.reservation.id).exists())
        self.schedule.refresh_from_db()
        self.assertEqual(self.schedule.confirmed_participants, 0)

    def test_delete_reservation__fail_with_invalid_user(self):
        # Given
        self.client.force_authenticate(user=self.other_user)
        url = self.get_url(self.reservation.id)

        # When
        response = self.client.delete(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())

    def test_delete_reservation__fail_with_unauthorized(self):
        # Given
        url = self.get_url(self.reservation.id)

        # When
        response = self.client.delete(url, format="json")

        # Then
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Reservation.objects.filter(id=self.reservation.id).exists())
