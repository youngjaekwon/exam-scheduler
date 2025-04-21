from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsAdminUserOrReadOnly
from schedules.models import ExamSchedule
from schedules.schemas import exam_schedule_schema_view
from schedules.serializers import ExamScheduleSerializer


@exam_schedule_schema_view
class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all()
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]
    filterset_fields = ["start_time", "end_time"]
    search_fields = ["title"]
    ordering_fields = ["title", "start_time"]
