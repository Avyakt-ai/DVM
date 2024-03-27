# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Dept
from django.contrib.auth.forms import UserCreationForm


class DepartmentSelectionForm(forms.Form):
    department = forms.ModelChoiceField(queryset=Dept.objects.all(), empty_label=None)
    sem = forms.IntegerField(min_value=1, max_value=8)  # Semester field


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
