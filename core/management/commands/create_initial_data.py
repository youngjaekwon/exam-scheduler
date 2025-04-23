from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils import timezone

from reservations.models import Reservation
from schedules.models import ExamSchedule

User = get_user_model()


class Command(BaseCommand):
    help = "Create initial data for testing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Creating initial data..."))

        # Create a superuser
        admin = self._create_superuser()

        # Create regular users
        users = self._create_users()

        # Create schedules
        schedules = self._create_schedules()

        # Create reservations
        self._create_reservations(schedules, users)

        self.stdout.write(self.style.WARNING("Initial data created."))

    def _create_superuser(self):
        self.stdout.write(self.style.WARNING("Creating superuser..."))
        admin, created = User.objects.get_or_create(
            username="adminuser",
            defaults={
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Superuser created."))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists."))

        return admin

    def _create_users(self):
        self.stdout.write(self.style.WARNING("Creating users..."))
        users = []

        for i in range(1, 3):
            user, created = User.objects.get_or_create(username=f"user{i}")
            if created:
                user.set_password("pass")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"User {i} created."))
            else:
                self.stdout.write(self.style.WARNING(f"User {i} already exists."))
            users.append(user)

        return users

    def _create_schedules(self):
        self.stdout.write(self.style.WARNING("Creating schedules..."))
        now = timezone.now()

        schedule1, s1_created = ExamSchedule.objects.get_or_create(
            title="예약 가능한 시험 for test",
            defaults={
                "description": "예약 가능한 시험",
                "start_time": now + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 2),
                "end_time": now + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 2, hours=2),
                "confirmed_participants": 0,
            },
        )

        schedule2, s2_created = ExamSchedule.objects.get_or_create(
            title="예약 마감된 시험 (일자) for test",
            defaults={
                "description": "시험 시작 시간으로 인해 예약 마감된 시험",
                "start_time": now + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS - 2),
                "end_time": now + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS - 2, hours=2),
                "confirmed_participants": 0,
            },
        )

        schedule3, s2_created_ = ExamSchedule.objects.get_or_create(
            title="예약 마감된 시험 (인원) for test",
            defaults={
                "description": "인원 으로 인해 예약 마감된 시험",
                "start_time": now + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 2),
                "end_time": now + timedelta(days=settings.EXAM_RESERVATION_DEADLINE_DAYS + 2, hours=2),
                "confirmed_participants": settings.EXAM_SCHEDULE_MAX_PARTICIPANTS,
            },
        )

        if any([s1_created, s2_created, s2_created_]):
            self.stdout.write(self.style.SUCCESS("Schedules created."))
        else:
            self.stdout.write(self.style.WARNING("Schedules already exist."))

        return [schedule1, schedule2, schedule3]

    def _create_reservations(self, schedules, users):
        self.stdout.write(self.style.WARNING("Creating reservations..."))

        # user1의 확정되지 않은 예약
        _, r1_created = Reservation.objects.get_or_create(
            user=users[0], schedule=schedules[0], expected_participants=10
        )

        # user1의 확정된 예약
        reservation, r2_created = Reservation.objects.get_or_create(
            user=users[0], schedule=schedules[0], expected_participants=100
        )
        if not reservation.is_confirmed:
            reservation.is_confirmed = True
            reservation.confirmed_at = timezone.now()
            reservation.save()
            schedules[0].confirmed_participants += reservation.expected_participants
            schedules[0].save()

        # user2의 확정되지 않은 예약
        _, r3_created = Reservation.objects.get_or_create(
            user=users[1], schedule=schedules[0], expected_participants=10
        )

        if any([r1_created, r2_created, r3_created]):
            self.stdout.write(self.style.SUCCESS("Reservations created."))
        else:
            self.stdout.write(self.style.WARNING("Reservations already exist."))
