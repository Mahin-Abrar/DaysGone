from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from drafts.utils import delete_draft, load_draft

from .forms import ExpenseForm
from .models import Category, Expense


def _get_categories(user):
    from django.db.models import Q
    return Category.objects.filter(Q(user=user) | Q(is_default=True, user__isnull=True))


@login_required
def expense_list(request):
    today = timezone.localdate()
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))

    expenses = Expense.objects.filter(
        user=request.user, date__year=year, date__month=month,
    ).select_related("category")

    by_category = (
        expenses.values("category__name", "category__color", "category__icon")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    days_in_month = monthrange(year, month)[1]
    daily_totals = {i: Decimal("0") for i in range(1, days_in_month + 1)}
    for row in expenses.values("date").annotate(total=Sum("amount")):
        daily_totals[row["date"].day] = row["total"]

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_total = Expense.objects.filter(
        user=request.user, date__year=prev_year, date__month=prev_month,
    ).aggregate(t=Sum("amount"))["t"] or Decimal("0")

    current_total = expenses.aggregate(t=Sum("amount"))["t"] or Decimal("0")

    chart_colors = ["#6366f1", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16"]

    return render(request, "expenses/list.html", {
        "expenses": expenses[:50],
        "by_category": list(by_category),
        "daily_totals": [float(daily_totals[d]) for d in range(1, days_in_month + 1)],
        "days_in_month": days_in_month,
        "month": month,
        "year": year,
        "current_total": current_total,
        "prev_total": float(prev_total),
        "chart_colors": chart_colors,
        "categories": _get_categories(request.user),
    })


@login_required
def expense_create(request):
    draft = load_draft(request.user.id, "expense")
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        form.fields["category"].queryset = _get_categories(request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            delete_draft(request.user.id, "expense")
            messages.success(request, "Expense added.")
            return redirect("expenses:list")
    else:
        initial = draft or {"date": timezone.localdate()}
        form = ExpenseForm(initial=initial)
        form.fields["category"].queryset = _get_categories(request.user)
    return render(request, "expenses/form.html", {
        "form": form,
        "draft": draft,
        "form_type": "expense",
    })


@login_required
@require_POST
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    messages.success(request, "Expense deleted.")
    return redirect("expenses:list")
