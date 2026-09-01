from django.conf import settings
from django.db import models


class Routine(models.Model):
    SCHEDULE_CHOICES = [
        ("daily", "Every day"),
        ("weekdays", "Weekdays only"),
        ("weekends", "Weekends only"),
        ("custom", "Custom days"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="routines")
    title = models.CharField(max_length=200)
    color = models.CharField(max_length=7, default="#6366f1")
    icon = models.CharField(max_length=10, default="✅")
    schedule = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default="daily")
    custom_days = models.CharField(max_length=20, blank=True, help_text="Comma-separated weekday numbers 0=Mon")
    target_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def is_due_on(self, date):
        if not self.is_active:
            return False
        weekday = date.weekday()
        if self.schedule == "daily":
            return True
        if self.schedule == "weekdays":
            return weekday < 5
        if self.schedule == "weekends":
            return weekday >= 5
        if self.schedule == "custom" and self.custom_days:
            allowed = {int(d.strip()) for d in self.custom_days.split(",") if d.strip().isdigit()}
            return weekday in allowed
        return False


class RoutineLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="routine_logs")
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name="logs")
    date = models.DateField()
    completed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "routine", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.routine.title} on {self.date}"
