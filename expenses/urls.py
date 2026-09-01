from django.urls import path

from .views import expense_create, expense_delete, expense_list

app_name = "expenses"

urlpatterns = [
    path("", expense_list, name="list"),
    path("new/", expense_create, name="create"),
    path("<int:pk>/delete/", expense_delete, name="delete"),
]
