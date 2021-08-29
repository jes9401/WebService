from django.db import models
from django.contrib.auth.models import User
from web.models import Info

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    twohand = models.IntegerField(default=0)
    waist = models.IntegerField(default=0)
    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

