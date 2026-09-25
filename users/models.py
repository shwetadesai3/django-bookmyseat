from django.db import models
class Movie(models.Model):
    name = models.CharField(max_length=200)
    trailer_url = models.URLField(blank=True, null=True)
# Create your models here.
