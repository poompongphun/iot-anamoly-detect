from django.db.models import Avg, Min, Max, StdDev
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from sensor.filter import SensorFilter
from sensor.models import Sensor
from sensor.serializers import SensorSerializer
from django_filters.rest_framework import DjangoFilterBackend
import numpy as np
import pandas as pd

# Create your views here.
class SensorDataModelViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.filter(
            temperature__isnull=False,
            humidity__isnull=False,
            air_quality__isnull=False
        ).values(
            'timestamp',
            'temperature',
            'humidity',
            'air_quality'
        ).order_by('timestamp').distinct()
    serializer_class = SensorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SensorFilter

    @action(detail=False, methods=['post'])
    def data(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def processed(self, request, *args, **kwargs):
        filtered_queryset = self.filter_queryset(self.get_queryset())

        stats = filtered_queryset.aggregate(
            avg_temperature=Avg('temperature'),
            std_temperature=StdDev('temperature'),
            avg_humidity=Avg('humidity'),
            std_humidity=StdDev('humidity'),
            avg_air_quality=Avg('air_quality'),
            std_air_quality=StdDev('air_quality')
        )

        def calc_z_score(value, avg, std):
            return (value - avg) / std if std else 0

        for sensor in filtered_queryset:
            for key in ['temperature', 'humidity', 'air_quality']:
                z_score = calc_z_score(sensor[key], stats['avg_' + key], stats['std_' + key])
                sensor[key] = {
                    "value": sensor[key],
                    "z_score": z_score,
                    "anomaly": abs(z_score) > 3
                }

        return Response(filtered_queryset)


    @action(detail=False, methods=['get'])
    def aggregated(self, request):
        filtered_queryset = self.filter_queryset(self.get_queryset())
        aggregated_data = filtered_queryset.aggregate(
            mean_temp=Avg('temperature'),
            min_temp=Min('temperature'),
            max_temp=Max('temperature'),
            sd_temp=StdDev('temperature'),
            mean_humidity=Avg('humidity'),
            min_humidity=Min('humidity'),
            max_humidity=Max('humidity'),
            sd_humidity=StdDev('humidity'),
            mean_air_quality=Avg('air_quality'),
            min_air_quality=Min('air_quality'),
            max_air_quality=Max('air_quality'),
            sd_air_quality=StdDev('air_quality')
        )

        df = pd.DataFrame(filtered_queryset)
        if not df.empty:
            df["temperature"] = df["temperature"].astype(float)
            df["humidity"] = df["humidity"].astype(float)
            df["air_quality"] = df["air_quality"].astype(float)

        response_data = {
            "temperature": {
                "mean": aggregated_data["mean_temp"],
                "median": df["temperature"].median() if not df.empty else None,
                "sd": aggregated_data["sd_temp"],
                "min": aggregated_data["min_temp"],
                "max": aggregated_data["max_temp"],
            },
            "humidity": {
                "mean": aggregated_data["mean_humidity"],
                "median": df["humidity"].median() if not df.empty else None,
                "sd": aggregated_data["sd_humidity"],
                "min": aggregated_data["min_humidity"],
                "max": aggregated_data["max_humidity"],
            },
            "air_quality": {
                "mean": aggregated_data["mean_air_quality"],
                "median": df["air_quality"].median() if not df.empty else None,
                "sd": aggregated_data["sd_air_quality"],
                "min": aggregated_data["min_air_quality"],
                "max": aggregated_data["max_air_quality"],
            }
        }

        return Response(response_data)
