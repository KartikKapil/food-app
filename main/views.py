from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import NewStudentForm, NewUserForm

# Create your views here.


@csrf_exempt
def signup(request):
    if request.method == "POST":
        userForm = NewUserForm(request.POST)
        newStudent = NewStudentForm(request.POST, request.FILES)
        # Keeing for future debugging, remove when stable
        #  print("userform non_field_errors: ")
        #  print(userForm.non_field_errors)
        #  print("userform field_errors: ")
        #  print([ (field.value, field.errors) for field in userForm] )
        #  print("student non_field_errors: ")
        #  print(userForm.non_field_errors)
        #  print("student field_errors: ")
        #  print([ (field.label, field.errors) for field in newStudent] )
        #  print("data: ")
        #  print(dict(request.POST))
        #  print("File: ")
        #  print(request.FILES)
        if userForm.is_valid() and newStudent.is_valid():
            userForm.save()
            newStudent.save()
            user = userForm.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            print("saved")
            return JsonResponse({'status': 'success'}, status=201)

        return JsonResponse({'status': 'failure'}, status=400)
    else:
        userForm = NewUserForm()
        newStudent = NewStudentForm()

    return render(request, 'main/signup.html', {'userForm': userForm, 'newStudent': newStudent})


def login(request):
    return HttpResponse('login page')


def home(request):
    return HttpResponse('hello world')
