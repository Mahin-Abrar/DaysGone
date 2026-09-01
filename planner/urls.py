from django.urls import path

from .views import (
    planner_carryover,
    planner_create,
    planner_delete,
    planner_move,
    planner_toggle,
    planner_view,
)

app_name = "planner"

urlpatterns = [
    path("", planner_view, name="list"),
    path("new/", planner_create, name="create"),
    path("<int:pk>/toggle/", planner_toggle, name="toggle"),
    path("<int:pk>/delete/", planner_delete, name="delete"),
    path("<int:pk>/move/<str:direction>/", planner_move, name="move"),
    path("carryover/", planner_carryover, name="carryover"),
]
