from django.urls import path

from .views import delete_draft_view, load_draft_view, save_draft_view

app_name = "drafts"

urlpatterns = [
    path("save/", save_draft_view, name="save"),
    path("load/", load_draft_view, name="load"),
    path("delete/", delete_draft_view, name="delete"),
]
