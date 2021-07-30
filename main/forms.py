from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields

from .models import Student


class NewUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username","password1", "password2"]


class NewStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class Document(forms.Form):
    menu = forms.FileField(label='Upload the menu')




