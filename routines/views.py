from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from rewards.models import Streak, check_missed_streaks, update_streak

from .forms import RoutineForm
from .icons import ROUTINE_ICONS
from .models import Routine, RoutineLog


def _today():
    return timezone.localdate()


@login_required
def routine_list(request):
    check_missed_streaks(request.user)
    today = _today()
    routines = Routine.objects.filter(user=request.user, is_active=True)
    due_routines = [r for r in routines if r.is_due_on(today)]
    completed_ids = set(
        RoutineLog.objects.filter(user=request.user, date=today).values_list("routine_id", flat=True)
    )

    routine_data = []
    for r in due_routines:
        streak_count = Streak.get_cached(request.user, r)
        routine_data.append({
            "routine": r,
            "completed": r.id in completed_ids,
            "streak": streak_count,
        })

    week_start = today - timedelta(days=today.weekday())
    heatmap = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        due = [r for r in routines if r.is_due_on(day)]
        done = RoutineLog.objects.filter(user=request.user, date=day).count()
        heatmap.append({
            "date": day,
            "label": day.strftime("%a"),
            "due": len(due),
            "done": done,
            "pct": int(done / len(due) * 100) if due else 0,
        })

    return render(request, "routines/list.html", {
        "routine_data": routine_data,
        "heatmap": heatmap,
        "today": today,
        "all_routines": routines,
    })


@login_required
def routine_create(request):
    if request.method == "POST":
        form = RoutineForm(request.POST)
        if form.is_valid():
            routine = form.save(commit=False)
            routine.user = request.user
            routine.save()
            messages.success(request, f"Routine '{routine.title}' created.")
            return redirect("routines:list")
    else:
        form = RoutineForm()
    return render(request, "routines/form.html", {
        "form": form, "title": "New Routine", "routine_icons": ROUTINE_ICONS,
    })


@login_required
def routine_edit(request, pk):
    routine = get_object_or_404(Routine, pk=pk, user=request.user)
    if request.method == "POST":
        form = RoutineForm(request.POST, instance=routine)
        if form.is_valid():
            form.save()
            messages.success(request, "Routine updated.")
            return redirect("routines:list")
    else:
        form = RoutineForm(instance=routine)
    return render(request, "routines/form.html", {
        "form": form, "title": "Edit Routine", "routine": routine, "routine_icons": ROUTINE_ICONS,
    })


@login_required
@require_POST
def routine_complete(request, pk):
    routine = get_object_or_404(Routine, pk=pk, user=request.user)
    today = _today()
    log, created = RoutineLog.objects.get_or_create(
        user=request.user, routine=routine, date=today,
    )
    new_badges = []
    if created:
        new_badges = update_streak(request.user, routine, today)

    streak_count = Streak.get_cached(request.user, routine)
    if request.htmx:
        return render(request, "routines/partials/routine_card.html", {
            "item": {"routine": routine, "completed": True, "streak": streak_count},
            "new_badges": new_badges,
        })
    return redirect("routines:list")


@login_required
@require_POST
def routine_uncomplete(request, pk):
    routine = get_object_or_404(Routine, pk=pk, user=request.user)
    today = _today()
    RoutineLog.objects.filter(user=request.user, routine=routine, date=today).delete()
    streak_count = Streak.get_cached(request.user, routine)
    if request.htmx:
        return render(request, "routines/partials/routine_card.html", {
            "item": {"routine": routine, "completed": False, "streak": streak_count},
        })
    return redirect("routines:list")


@login_required
@require_POST
def routine_delete(request, pk):
    routine = get_object_or_404(Routine, pk=pk, user=request.user)
    routine.delete()
    if request.htmx:
        return HttpResponse("")
    messages.success(request, "Routine deleted.")
    return redirect("routines:list")
