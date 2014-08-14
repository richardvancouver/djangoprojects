from django.db import models

# Create your models here.

class AD(models.Model):
    title = models.CharField(max_length=200)
    loc = models.CharField(max_length=100)
    url = models.CharField(max_length=200, primary_key=True)
    rating = models.FloatField()
    date = models.CharField(max_length=10)
    price = models.IntegerField()
    line = models.CharField(max_length=500)
    dist = models.FloatField()
