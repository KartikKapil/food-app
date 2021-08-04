from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import DocumentForm, NewStudentForm, NewUserForm
from .models import *
import csv
# Create your views here.

def handle_uploaded_file(f,username):
    fields = []
    objects = []

    with open('try.csv','wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    with open('try.csv','r') as destination:
        csvreader = csv.reader(destination)
        next(csvreader)
        for j in range(6):
            fields = next(csvreader)
            objects.append(fields)

    time_of_the_day=['Breakfast','Lunch','Dinner']
    user = User.objects.get(username=username)
    student_name = user.student.name
    student = Student.objects.get(name = student_name)
    # print("\n Student name is :")
    # print(student_name)
    for items in objects:
        i=1
        for time in time_of_the_day:
            newDoc = Document(user=student,Day_of_name=items[0],Time=time,food_item_name=items[i])
            i = i+1
            newDoc.save()

@csrf_exempt
def signup(request):
    if request.method == "POST":
        userForm = NewUserForm(request.POST)
        newStudent = NewStudentForm(request.POST)
        newDocument = DocumentForm(request.POST,request.FILES)

        # Keeing for future debugging, remove when stable
        #  print("userform non_field_errors: ")
        #  print(userForm.non_field_errors)
        #  print("userform field_errors: ")
        #  print([ (field.value, field.errors) for field in userForm] )

        #  print("student non_field_errors: ")
        #  print(newStudent.non_field_errors)
        #  print("student field_errors: ")
        #  print([ (field.label, field.errors) for field in newStudent] )

        #  print("document non_field_errors: ")
        #  print(newDocument.non_field_errors)
        # print("document field_errors: ")
        # print([ (field.label, field.errors) for field in newDocument] )

        print("userForm.is_valid(): ")
        print(userForm.is_valid())
        print("newStudent.is_valid(): ")
        print(newStudent.is_valid())
        print("newDocument.is_valid(): ")
        print(newDocument.is_valid())

        #  print("data: ")
        #  print(dict(request.POST))
        #  print("File: ")
        #  print(request.FILES)

        if userForm.is_valid() and newStudent.is_valid() and newDocument.is_valid():
            user = userForm.save()
            student = newStudent.save(commit=False)
            student.user = user
            student.save()
            # newDocument.save()
            user = userForm.cleaned_data.get('username')
            handle_uploaded_file(request.FILES['file'],user)
            messages.success(request, 'Account was created for ' + user)
            print("saved")
            return JsonResponse({'status': 'success'}, status=201)

        return JsonResponse({'status': 'failure'}, status=400)
    else:
        userForm = NewUserForm()
        newStudent = NewStudentForm()
        newDocument = DocumentForm()

    return render(request, 'main/signup.html',
                  {'userForm': userForm, 'newStudent': newStudent, 'newDocument': newDocument})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f' wecome {username} !!')
            return JsonResponse({'status': 'success'}, status=200)
        else:
            return JsonResponse({'status': 'failure'}, status=403)
    return HttpResponse('login page')


def home(request):
    return HttpResponse('hello world')


def customer(request, pk_test):
    user = User.objects.get(username=pk_test)
    student_name = user.student.name
    student_budget = user.student.budget
    student_preferred_restaurants = user.student.preferred_restaurants
    student_preferred_cuisines = user.student.preferred_cuisines
    student_not_preferred = user.student.not_preferred
    return HttpResponse('a little work left') 
