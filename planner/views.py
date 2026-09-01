from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from drafts.utils import delete_draft, load_draft

from .forms import PlannerItemForm
from .models import PlannerItem


def _tomorrow():
    return timezone.localdate() + timedelta(days=1)


@login_required
def planner_view(request):
    target = request.GET.get("date")
    if target:
        from datetime import datetime
        target_date = datetime.strptime(target, "%Y-%m-%d").date()
    else:
        target_date = _tomorrow()

    items = PlannerItem.objects.filter(user=request.user, target_date=target_date)
    blocks = {
        "morning": items.filter(time_block="morning"),
        "afternoon": items.filter(time_block="afternoon"),
        "evening": items.filter(time_block="evening"),
        "anytime": items.filter(time_block="anytime"),
    }
    return render(request, "planner/list.html", {
        "blocks": blocks,
        "target_date": target_date,
        "tomorrow": _tomorrow(),
    })


@login_required
def planner_create(request):
    draft = load_draft(request.user.id, "planner")
    if request.method == "POST":
        form = PlannerItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            if not item.target_date:
                item.target_date = _tomorrow()
            item.order = PlannerItem.objects.filter(
                user=request.user, target_date=item.target_date,
            ).count()
            item.save()
            delete_draft(request.user.id, "planner")
            messages.success(request, "Planner item added.")
            return redirect("planner:list")
    else:
        initial = draft or {"target_date": _tomorrow()}
        form = PlannerItemForm(initial=initial)
    return render(request, "planner/form.html", {
        "form": form,
        "draft": draft,
        "form_type": "planner",
    })


@login_required
@require_POST
def planner_toggle(request, pk):
    item = get_object_or_404(PlannerItem, pk=pk, user=request.user)
    item.is_done = not item.is_done
    item.save()
    if request.htmx:
        return render(request, "planner/partials/item.html", {"item": item})
    return redirect("planner:list")


@login_required
@require_POST
def planner_delete(request, pk):
    item = get_object_or_404(PlannerItem, pk=pk, user=request.user)
    item.delete()
    if request.htmx:
        from django.http import HttpResponse
        return HttpResponse("")
    return redirect("planner:list")


@login_required
@require_POST
def planner_move(request, pk, direction):
    item = get_object_or_404(PlannerItem, pk=pk, user=request.user)
    siblings = list(
        PlannerItem.objects.filter(
            user=request.user, target_date=item.target_date, time_block=item.time_block,
        ).order_by("order", "pk")
    )
    idx = next(i for i, s in enumerate(siblings) if s.pk == item.pk)
    if direction == "up" and idx > 0:
        siblings[idx], siblings[idx - 1] = siblings[idx - 1], siblings[idx]
    elif direction == "down" and idx < len(siblings) - 1:
        siblings[idx], siblings[idx + 1] = siblings[idx + 1], siblings[idx]
    for i, s in enumerate(siblings):
        PlannerItem.objects.filter(pk=s.pk).update(order=i)
    return redirect("planner:list")


@login_required
@require_POST
def planner_carryover(request):
    today = timezone.localdate()
    unfinished = PlannerItem.objects.filter(user=request.user, target_date=today, is_done=False)
    tomorrow = _tomorrow()
    count = 0
    for item in unfinished:
        item.pk = None
        item.target_date = tomorrow
        item.is_done = False
        item.order = PlannerItem.objects.filter(user=request.user, target_date=tomorrow).count()
        item.save()
        count += 1
    messages.success(request, f"Carried over {count} item(s) to tomorrow.")
    return redirect("planner:list")
