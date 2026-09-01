from django import forms

from .models import Routine

INPUT_CLASS = "w-full px-4 py-2 rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 outline-none"


class RoutineForm(forms.ModelForm):
    class Meta:
        model = Routine
        fields = ("title", "color", "icon", "schedule", "custom_days", "target_time", "is_active")
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "color": forms.TextInput(attrs={"type": "color", "class": "w-16 h-10 rounded cursor-pointer"}),
            "icon": forms.HiddenInput(),
            "schedule": forms.Select(attrs={"class": INPUT_CLASS}),
            "custom_days": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "0,1,2 = Mon,Tue,Wed"}),
            "target_time": forms.TimeInput(attrs={"type": "time", "class": INPUT_CLASS}),
            "is_active": forms.CheckboxInput(attrs={"class": "w-4 h-4"}),
        }
