from django import forms

from .models import PlannerItem

INPUT_CLASS = "w-full px-4 py-2 rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 outline-none"


class PlannerItemForm(forms.ModelForm):
    class Meta:
        model = PlannerItem
        fields = ("title", "priority", "time_block", "target_date")
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "priority": forms.Select(attrs={"class": INPUT_CLASS}),
            "time_block": forms.Select(attrs={"class": INPUT_CLASS}),
            "target_date": forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        }
