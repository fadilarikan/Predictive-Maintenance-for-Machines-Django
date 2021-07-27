from django.db import models
from django.db.models import Model

class Predict(Model):
    vibration_y = models.FloatField()
    pressure_6h_mean = models.FloatField()
    temperature_6h_std = models.FloatField()

    def __float__(self):
        return self.vibration_y, self.pressure_6h_mean, self.temperature_6h_std



    class Meta:
        verbose_name_plural = 'predicts'

# Create your models here.
