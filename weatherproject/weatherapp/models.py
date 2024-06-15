
from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100)
    temperature = models.FloatField(null=True, blank=True) 

    def __str__(self):
        return self.name
