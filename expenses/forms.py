from django import forms

from .models import Expense

INPUT_CLASS = "w-full px-4 py-2 rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 outline-none"


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ("category", "amount", "date", "note", "payment_method")
        widgets = {
            "category": forms.Select(attrs={"class": INPUT_CLASS}),
            "amount": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "date": forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
            "note": forms.Textarea(attrs={"rows": 2, "class": INPUT_CLASS}),
            "payment_method": forms.Select(attrs={"class": INPUT_CLASS}),
        }
