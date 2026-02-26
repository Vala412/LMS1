from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"



class Author(models.Model):
    name = models.CharField(max_length=250)
    birth_date = models.DateField(blank=True, null=True)
    profile = models.OneToOneField(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='author')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name