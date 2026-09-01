from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from rewards.models import Badge, Streak, UserBadge


@login_required
def rewards_view(request):
    badges = Badge.objects.all()
    earned = UserBadge.objects.filter(user=request.user).select_related("badge", "routine")
    earned_ids = set(earned.values_list("badge_id", flat=True))
    streaks = Streak.objects.filter(user=request.user).select_related("routine").order_by("-current_streak")

    return render(request, "rewards/list.html", {
        "badges": badges,
        "earned": earned,
        "earned_ids": earned_ids,
        "streaks": streaks,
    })
