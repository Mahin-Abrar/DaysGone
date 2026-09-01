from django.conf import settings
from django.db import models


class PlannerItem(models.Model):
    PRIORITY_CHOICES = [
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]
    TIME_BLOCK_CHOICES = [
        ("morning", "Morning"),
        ("afternoon", "Afternoon"),
        ("evening", "Evening"),
        ("anytime", "Anytime"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="planner_items")
    target_date = models.DateField()
    title = models.CharField(max_length=300)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    time_block = models.CharField(max_length=20, choices=TIME_BLOCK_CHOICES, default="anytime")
    is_done = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["target_date", "order", "pk"]

    def __str__(self):
        return f"{self.title} ({self.target_date})"
