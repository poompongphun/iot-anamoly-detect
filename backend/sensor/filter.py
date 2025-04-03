from django_filters import rest_framework as filters

class SensorFilter(filters.FilterSet):
    timestamp = filters.DateTimeFromToRangeFilter(field_name="timestamp")
