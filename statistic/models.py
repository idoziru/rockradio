from collections import Counter
from django.db import models
from django.dispatch import receiver


class Spider(models.Model):
    name = models.CharField(blank=False, unique=True, max_length=255)
    visits_counter = models.IntegerField(default=0)

    def __str__(self):
        return self.name
