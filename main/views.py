import django
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import NewStudentForm,NewUserForm
from django.contrib import messages

# Create your views here.

def signup(request):
    if request.method == "POST":
        userForm = NewUserForm(request.POST)
        newStudent = NewStudentForm(request.POST)
        if userForm.is_valid() and newStudent.is_valid():
            userForm.save()
            newStudent.save()
            user = userForm.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            
            redirect('login')
    else:
        userForm = NewUserForm()
        newStudent = NewStudentForm()
    
    return render(request,'main/signup.html',{'userForm':userForm,'newStudent':newStudent})

def login(request):
    return HttpResponse('login page')

def home(request):
    return HttpResponse('hello world')
