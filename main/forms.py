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
        fields = ["name", "address", "phone", "budget", "preferred_restuarnt", "preferred_cusine", "not_preferred"]

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = "__all__"




