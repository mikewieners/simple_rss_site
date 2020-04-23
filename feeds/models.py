from django.db import models


class Feed(models.Model):
    url = models.CharField(max_length=300)
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name
