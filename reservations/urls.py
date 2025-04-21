from rest_framework.routers import DefaultRouter

from reservations.views import ReservationViewSet

app_name = "reservations"
router = DefaultRouter()
router.register("reservations", ReservationViewSet, basename="reservations")
urlpatterns = router.urls
