from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Student, User, Vendor


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

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = '__all__'


