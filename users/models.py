# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)

    partner = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username
    
    def get_partner(self):
        return self.partner

class Friendship(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendship_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} (Accepted: {self.accepted})"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    url = models.URLField(blank=True, null=True)
    viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_match_notification = models.BooleanField(default=False) # Добавлено новое поле

    def __str__(self):
        return self.title