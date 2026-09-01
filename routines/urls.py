from django.urls import path

from .views import (
    routine_complete,
    routine_create,
    routine_delete,
    routine_edit,
    routine_list,
    routine_uncomplete,
)

app_name = "routines"

urlpatterns = [
    path("", routine_list, name="list"),
    path("new/", routine_create, name="create"),
    path("<int:pk>/edit/", routine_edit, name="edit"),
    path("<int:pk>/complete/", routine_complete, name="complete"),
    path("<int:pk>/uncomplete/", routine_uncomplete, name="uncomplete"),
    path("<int:pk>/delete/", routine_delete, name="delete"),
]
