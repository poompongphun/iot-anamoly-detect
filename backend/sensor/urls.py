from django.urls import path, include
from rest_framework import routers
from sensor import views

router = routers.DefaultRouter()

router.register(r"", views.SensorDataModelViewSet, basename="sensor")

urlpatterns = [
    path("", include(router.urls)),
]