from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    age = models.IntegerField(null=True, blank=True)
    gender = models.IntegerField(null=True, blank=True)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    activity_level = models.CharField(max_length=50, blank=True)
    goal = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
