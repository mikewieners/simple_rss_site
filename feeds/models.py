from django.db import models
from django.contrib.auth.models import User


class Feed(models.Model):
    url = models.CharField(max_length=300)
    name = models.CharField(max_length=300)

    # Subscribed
    subscribers = models.ManyToManyField(User)

    def __str__(self):
        return self.name
