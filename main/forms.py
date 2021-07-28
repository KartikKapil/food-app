from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields
from .models import Customer

class NewUserForm(UserCreationForm):

    class Meta:
        models = User
        fields = ["username","password1", "password2"]


class NewStudentForm(forms.ModelForm):
    class Meta:
        mdoel = Customer
        fields = '__all__'




