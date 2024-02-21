# models.py
from django.db import models

class Slider(models.Model):
    images = models.ImageField(upload_to="photos/slider")

    def __str__(self):
        return f"Slider Image - {self.images.name}"
