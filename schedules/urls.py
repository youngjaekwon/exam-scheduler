from rest_framework.routers import DefaultRouter

from schedules.views import ExamScheduleViewSet

app_name = "schedules"

router = DefaultRouter()
router.register("exam-schedules", ExamScheduleViewSet, basename="exam-schedules")
urlpatterns = router.urls
