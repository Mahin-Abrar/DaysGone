from django.urls import path

from .views import rewards_view

app_name = "rewards"

urlpatterns = [
    path("", rewards_view, name="list"),
]
