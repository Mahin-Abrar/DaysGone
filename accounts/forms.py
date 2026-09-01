from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .avatars import AVATAR_EMOJIS
from .models import Profile

INPUT_CLASS = "w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 dark:bg-gray-700/50 outline-none focus:ring-2 focus:ring-indigo-500/40 transition"


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProfileForm(forms.ModelForm):
    avatar = forms.ChoiceField(
        choices=[(e, e) for e in AVATAR_EMOJIS],
        widget=forms.RadioSelect(attrs={"class": "avatar-radio hidden"}),
    )

    class Meta:
        model = Profile
        fields = ("avatar", "avatar_color", "timezone", "currency")
        widgets = {
            "avatar_color": forms.HiddenInput(),
            "timezone": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "currency": forms.Select(attrs={"class": INPUT_CLASS}),
        }
