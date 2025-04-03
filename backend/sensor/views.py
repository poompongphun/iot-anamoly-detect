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
        ).order_by('-timestamp').distinct()
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
            avg_temperature=Avg('temperature'), std_temperature=StdDev('temperature'),
            avg_humidity=Avg('humidity'), std_humidity=StdDev('humidity'),
            avg_air_quality=Avg('air_quality'), std_air_quality=StdDev('air_quality')
        )

        for sensor in filtered_queryset:
            z_temp = (sensor['temperature'] - stats['avg_temperature']) / stats['std_temperature'] if stats['std_temperature'] else 0
            z_humidity = (sensor['humidity'] - stats['avg_humidity']) / stats['std_humidity'] if stats['std_humidity'] else 0
            z_air_quality = (sensor['air_quality'] - stats['avg_air_quality']) / stats['std_air_quality'] if stats['std_air_quality'] else 0

            sensor['z_scores'] = {
                'temperature': z_temp,
                'humidity': z_humidity,
                'air_quality': z_air_quality
            }

            sensor['anomaly'] = abs(z_temp) > 3 or abs(z_humidity) > 3 or abs(z_air_quality) > 3

        return Response(filtered_queryset)


    @action(detail=False, methods=['get'])
    def aggregated(self, request):
        filtered_queryset = self.filter_queryset(self.get_queryset())
        aggregated_data = filtered_queryset.aggregate(
            mean_temp=Avg('temperature'),
            min_temp=Min('temperature'),
            max_temp=Max('temperature'),
            mean_humidity=Avg('humidity'),
            min_humidity=Min('humidity'),
            max_humidity=Max('humidity'),
            mean_air_quality=Avg('air_quality'),
            min_air_quality=Min('air_quality'),
            max_air_quality=Max('air_quality'),
        )

        temperatures = list(filtered_queryset.values_list('temperature', flat=True))
        humidities = list(filtered_queryset.values_list('humidity', flat=True))
        air_qualities = list(filtered_queryset.values_list('air_quality', flat=True))

        def safe_median(data):
            data = [x for x in data if x is not None]
            return float(np.median(data)) if data else None

        response_data = {
            "temperature": {
                "mean": aggregated_data["mean_temp"],
                "median": safe_median(temperatures),
                "min": aggregated_data["min_temp"],
                "max": aggregated_data["max_temp"],
            },
            "humidity": {
                "mean": aggregated_data["mean_humidity"],
                "median": safe_median(humidities),
                "min": aggregated_data["min_humidity"],
                "max": aggregated_data["max_humidity"],
            },
            "air_quality": {
                "mean": aggregated_data["mean_air_quality"],
                "median": safe_median(air_qualities),
                "min": aggregated_data["min_air_quality"],
                "max": aggregated_data["max_air_quality"],
            }
        }

        return Response(response_data)
