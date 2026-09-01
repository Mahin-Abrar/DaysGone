from django.conf import settings
from django.db import models

from .avatars import DEFAULT_AVATAR


class Profile(models.Model):
    CURRENCY_CHOICES = [
        ("BDT", "৳ BDT"),
        ("USD", "$ USD"),
        ("EUR", "€ EUR"),
        ("GBP", "£ GBP"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    avatar = models.CharField(max_length=10, default=DEFAULT_AVATAR)
    avatar_color = models.CharField(max_length=7, default="#6366f1")
    timezone = models.CharField(max_length=64, default="Asia/Dhaka")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="BDT")

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def display_avatar(self):
        return self.avatar or DEFAULT_AVATAR
