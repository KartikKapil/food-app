from datetime import datetime
from rest_framework import parsers
from rest_framework.parsers import FileUploadParser,MultiPartParser
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework import response
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from .forms import DocumentForm, NewStudentForm, NewUserForm
from .models import Menu, Student
from .recommend import recommend as recommend_dish
from .serializers import (
    StudentSerializer, UserSerializer, UserSerializerWithToken, VendorSerializer
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
def Mess_menu_upload(request):
    username = request.POST.get('username')
    parser_classes = [FileUploadParser]
    file_obj = request.data['file']
    if len(file_obj)!=0:
        handle_uploaded_file(file_obj,username)
        response = {
        "User":username
        }
        return Response(response,status=204)
    else:
        user=User.objects.get(username=username)
        user.delete()
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
        mess_menu = Menu.objects.get(student=student, day=today, time="lunch").dishes
    except ObjectDoesNotExist:
        # object does not exists
        return JsonResponse({'status': 'failure'}, status=403)

    restrs = [{"name": "abc", "price": 120}, {"name": "def", "price": 300}]

    # Get the recommendation
    recommendation = recommend_dish(budget_total, budget_spent, restrs, dislikes, mess_menu)

    return JsonResponse(recommendation)
