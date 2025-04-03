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
            avg_temperature=Avg('temperature'), std_temperature=StdDev('temperature'),
            avg_humidity=Avg('humidity'), std_humidity=StdDev('humidity'),
            avg_air_quality=Avg('air_quality'), std_air_quality=StdDev('air_quality')
        )

        for sensor in filtered_queryset:
            z_temp = (sensor['temperature'] - stats['avg_temperature']) / stats['std_temperature'] if stats['std_temperature'] else 0
            z_humidity = (sensor['humidity'] - stats['avg_humidity']) / stats['std_humidity'] if stats['std_humidity'] else 0
            z_air_quality = (sensor['air_quality'] - stats['avg_air_quality']) / stats['std_air_quality'] if stats['std_air_quality'] else 0

            tmp_temperature = {
                "value": sensor['temperature'],
                "z_score": z_temp,
                "anomaly": abs(z_temp) > 3
            }
            tmp_humidity = {
                "value": sensor['humidity'],
                "z_score": z_humidity,
                "anomaly": abs(z_humidity) > 3
            }
            tmp_air_quality = {
                "value": sensor['air_quality'],
                "z_score": z_air_quality,
                "anomaly": abs(z_air_quality) > 3
            }
            sensor['temperature'] = tmp_temperature
            sensor['humidity'] = tmp_humidity
            sensor['air_quality'] = tmp_air_quality

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
            return {"median": float(np.median(data)), "sd": float(np.std(data))} if data else None

        tempAgg = safe_median(temperatures)
        humiAgg = safe_median(humidities)
        airAgg = safe_median(air_qualities)

        response_data = {
            "temperature": {
                "mean": aggregated_data["mean_temp"],
                "median": tempAgg['median'] if tempAgg else None,
                "sd": tempAgg['sd'] if tempAgg else None,
                "min": aggregated_data["min_temp"],
                "max": aggregated_data["max_temp"],
            },
            "humidity": {
                "mean": aggregated_data["mean_humidity"],
                "median": humiAgg['median'] if humiAgg else None,
                "sd": humiAgg['sd'] if humiAgg else None,
                "min": aggregated_data["min_humidity"],
                "max": aggregated_data["max_humidity"],
            },
            "air_quality": {
                "mean": aggregated_data["mean_air_quality"],
                "median": airAgg['median'] if airAgg else None,
                "sd": airAgg['sd'] if airAgg else None,
                "min": aggregated_data["min_air_quality"],
                "max": aggregated_data["max_air_quality"],
            }
        }

        return Response(response_data)
