from django.db import models
from django.contrib.auth.models import User


class Feed(models.Model):
    url = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=1000, null=True)
    logo = models.CharField(max_length=500, null=True)

    # Subscribed
    subscribers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name
