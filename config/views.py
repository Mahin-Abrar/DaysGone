from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from expenses.models import Expense
from planner.models import PlannerItem
from rewards.models import Streak, UserBadge
from routines.models import Routine, RoutineLog


@login_required
def dashboard(request):
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    routines = Routine.objects.filter(user=request.user, is_active=True)
    due_today = [r for r in routines if r.is_due_on(today)]
    completed_today = RoutineLog.objects.filter(user=request.user, date=today).count()
    total_due = len(due_today)
    progress_pct = int(completed_today / total_due * 100) if total_due else 0

    top_streaks = Streak.objects.filter(user=request.user, current_streak__gt=0).select_related("routine")[:5]

    month_expenses = Expense.objects.filter(
        user=request.user, date__year=today.year, date__month=today.month,
    )
    month_total = month_expenses.aggregate(t=Sum("amount"))["t"] or Decimal("0")
    by_category = (
        month_expenses.values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:5]
    )

    tomorrow_items = PlannerItem.objects.filter(user=request.user, target_date=tomorrow, is_done=False)[:5]
    recent_badges = UserBadge.objects.filter(user=request.user).select_related("badge")[:3]

    return render(request, "dashboard.html", {
        "today": today,
        "tomorrow": tomorrow,
        "completed_today": completed_today,
        "total_due": total_due,
        "progress_pct": progress_pct,
        "top_streaks": top_streaks,
        "month_total": month_total,
        "by_category": list(by_category),
        "tomorrow_items": tomorrow_items,
        "recent_badges": recent_badges,
        "currency": request.user.profile.currency,
    })
