from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields

from .models import Document, Student


class NewUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username","password1", "password2"]


class NewStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "address", "phone", "budget_total", "preferred_restaurants", "preferred_cuisines", "not_preferred"]

class DocumentForm(forms.Form):
    # title = forms.CharField(max_length=50)
    file = forms.FileField()



