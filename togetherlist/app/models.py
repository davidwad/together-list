from django.db import models
from django.contrib.auth.models import User


class Track(models.Model):
    spotify_id = models.CharField(max_length=50)
    title = models.CharField(max_length=70)
    artist_names = models.JSONField()
    votes = models.ManyToManyField(User)

    def __str__(self):
        return ', '.join(self.artist_names) + ' - ' + self.title


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track_id = models.CharField(max_length=50)
