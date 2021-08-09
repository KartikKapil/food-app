from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import parsers, permissions, response, status
from rest_framework.decorators import (
    api_view, parser_classes, permission_classes
)
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response

from .forms import DocumentForm, NewStudentForm, NewUserForm
from .models import Menu, Student
from .recommend import recommend as recommend_dish
from .serializers import (
    StudentSerializer, UserSerializer, UserSerializerWithToken,
    VendorSerializer
)
from .utility import get_restaurants, handle_uploaded_file


def not_loged_in(request):
    return JsonResponse({'status': 'failure'}, status=400)


@api_view(['GET'])
def current_user(request):

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def user_create(request):
    serializer = UserSerializerWithToken(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def new_signup(request):
    # Get the serialized data
    user_serializer = UserSerializerWithToken(data=request.data)
    student_serializer = StudentSerializer(data=request.data)

    # Save the data if Valid
    if user_serializer.is_valid() and student_serializer.is_valid():
        user = user_serializer.save()
        student_serializer.save(user=user)
        response = {
            "user": user_serializer.data,
            "student": student_serializer.data
        }
        return Response(response, status=status.HTTP_201_CREATED)

    # Make sure is_valid is called for each serializer
    user_serializer.is_valid()
    student_serializer.is_valid()

    # Return the errors as a JSON Response
    errors = {
        "user": user_serializer.errors,
        "student": student_serializer.errors
    }
    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def new_vendor_signup(request):
    user_serializer = UserSerializerWithToken(data=request.data)
    vendor_serializer = VendorSerializer(data=request.data)

    if user_serializer.is_valid() and vendor_serializer.is_valid():
        user = user_serializer.save()
        vendor_serializer.save(user=user)
        response = {
            "user":user_serializer.data,
            "vendor":vendor_serializer.data
        }
        return Response(response, status=status.HTTP_201_CREATED)
    print('user_serializer.is_valid():')
    print(user_serializer.is_valid())
    print('vendor_serializer.is_valid():')
    print(vendor_serializer.is_valid())
    errors = {
        "user":user_serializer.errors,
        "vendors":vendor_serializer.errors
    }
    return Response(errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def handle_files(request):
    username = request.POST.get('username')
    parser_classes = [FileUploadParser]
    file_obj = request.data['file']
    response = {
        "User":username
    }
    return Response(response,status=204)


@csrf_exempt
def signup(request):
    if request.method == "POST":
        userForm = NewUserForm(request.POST)
        newStudent = NewStudentForm(request.POST)
        newDocument = DocumentForm(request.POST, request.FILES)

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
        #  print("document field_errors: ")
        #  print([ (field.label, field.errors) for field in newDocument] )

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

            username = userForm.cleaned_data.get('username')
            handle_uploaded_file(request.FILES['file'], username)
            get_restaurants(request.POST["preferred_restaurants"], username)

            messages.success(request, 'Account was created for ' + username)
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


@login_required(login_url='/not_loged_in/')
def recommend(request, username):
    # Fetch the required data
    user = User.objects.get(username=username)
    student = user.student

    budget_total = user.student.budget_total
    budget_spent = user.student.budget_spent
    preferred_restaurants = user.student.preferred_restaurants
    preferred_cuisines = user.student.preferred_cuisines
    dislikes = user.student.not_preferred

    today = datetime.now().strftime("%w")
    try:
        mess_menu = Document.objects.get(student=student, day=today, time="lunch").dishes
    except ObjectDoesNotExist:
        # object does not exists
        return JsonResponse({'status': 'failure'}, status=403)

    restrs = [{"name": "abc", "price": 120}, {"name": "def", "price": 300}]

    # Get the recommendation
    recommendation = recommend_dish(budget_total, budget_spent, restrs, dislikes, mess_menu)

    return JsonResponse(recommendation)
