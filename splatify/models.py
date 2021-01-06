from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from social_django.models import UserSocialAuth

# Create your models here.
class Profile(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    fave_artists = models.ManyToManyField('Artist', through="TopArtist")
    populated = models.BooleanField(default=False)

class Artist(models.Model):
    name = models.CharField(max_length=100)
    spotify_id = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True)
    popularity = models.IntegerField() 
    uri = models.CharField(max_length=100)
    related = models.ManyToManyField("self")

class TopArtist(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    affinity = models.IntegerField()

class RelatedArtist(models.Model):
    root_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="root_artist")
    artist2 = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="related_artist")
    affinity = models.IntegerField()

from .spopulate import get_top_artists

@receiver(post_save, sender=UserSocialAuth)
def create_profile(sender, created, instance, **kwargs):
    if created:
        profile = Profile.objects.create(account=instance.user)





