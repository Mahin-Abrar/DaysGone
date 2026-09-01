from django.contrib import admin

from expenses.models import Category, Expense
from planner.models import PlannerItem
from rewards.models import Badge, Streak, UserBadge
from routines.models import Routine, RoutineLog

admin.site.register(Routine)
admin.site.register(RoutineLog)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(PlannerItem)
admin.site.register(Badge)
admin.site.register(Streak)
admin.site.register(UserBadge)
