from django.db import models

# Create your models here.
class Sensor(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    humidity = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    air_quality = models.DecimalField(max_digits=15, decimal_places=2, null=True)
