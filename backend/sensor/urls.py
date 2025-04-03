from django.urls import path, include
from rest_framework import routers
from sensor import views

router = routers.DefaultRouter()

router.register(r"", views.SensorDataModelViewSet, basename="sensor")

urlpatterns = [
    path("", include(router.urls)),
    # path("data", views.SensorDataAPIView.as_view(), name="sensor-data"),
    # path("processed", views.SensorProcessedAPIView.as_view(), name="sensor-processed"),
    # path("aggregated", views.SensorAggregatedAPIView.as_view(), name="sensor-aggregated"),
]