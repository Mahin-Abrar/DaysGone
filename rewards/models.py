from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default="🏆")
    milestone_days = models.PositiveIntegerField(unique=True)
    color = models.CharField(max_length=7, default="#f59e0b")

    class Meta:
        ordering = ["milestone_days"]

    def __str__(self):
        return f"{self.name} ({self.milestone_days} days)"


class Streak(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streaks")
    routine = models.ForeignKey("routines.Routine", on_delete=models.CASCADE, related_name="streaks")
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_completed_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "routine")

    def __str__(self):
        return f"{self.user.username} - {self.routine.title}: {self.current_streak}"

    @classmethod
    def get_cached(cls, user, routine):
        key = f"streak:{user.id}:{routine.id}"
        data = cache.get(key)
        if data is not None:
            return data
        streak, _ = cls.objects.get_or_create(user=user, routine=routine)
        cache.set(key, streak.current_streak, 300)
        return streak.current_streak

    @classmethod
    def invalidate_cache(cls, user, routine):
        cache.delete(f"streak:{user.id}:{routine.id}")


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    routine = models.ForeignKey("routines.Routine", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ("user", "badge", "routine")

    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"


def update_streak(user, routine, completed_date):
    """Recalculate streak after a routine is completed."""
    streak, _ = Streak.objects.get_or_create(user=user, routine=routine)
    new_badges = []

    if streak.last_completed_date == completed_date:
        Streak.invalidate_cache(user, routine)
        return new_badges

    if streak.last_completed_date:
        expected = streak.last_completed_date + timedelta(days=1)
        while not routine.is_due_on(expected) and expected < completed_date:
            expected += timedelta(days=1)
        if expected == completed_date:
            streak.current_streak += 1
        elif streak.last_completed_date == completed_date - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
    else:
        streak.current_streak = 1

    streak.last_completed_date = completed_date
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    streak.save()

    for badge in Badge.objects.filter(milestone_days__lte=streak.current_streak):
        _, created = UserBadge.objects.get_or_create(
            user=user, badge=badge, routine=routine,
            defaults={"earned_at": timezone.now()},
        )
        if created:
            new_badges.append(badge)

    Streak.invalidate_cache(user, routine)
    return new_badges


def check_missed_streaks(user):
    """Reset streaks where scheduled days were missed."""
    today = timezone.localdate()
    for streak in Streak.objects.filter(user=user, last_completed_date__isnull=False):
        routine = streak.routine
        if not routine.is_active:
            continue
        check_date = streak.last_completed_date + timedelta(days=1)
        while check_date < today:
            if routine.is_due_on(check_date):
                streak.current_streak = 0
                streak.save()
                Streak.invalidate_cache(user, routine)
                break
            check_date += timedelta(days=1)
