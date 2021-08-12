import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import password_validation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, parsers, permissions, response, status
from rest_framework.decorators import (
    api_view, parser_classes, permission_classes
)
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import DocumentForm, NewStudentForm, NewUserForm
from .models import Menu, Student, Transcations, Vendor
from .recommend import recommend as recommend_dish
from .serializers import (
    ChangePasswordSerializer, StudentSerializer, UserSerializer,
    UserSerializerWithToken, VendorSerializer
)
from .utility import (
    Distance_between_user_and_vendors, get_restaurants, handle_uploaded_file
)


def not_loged_in(request):
    return JsonResponse({'status': 'failure'}, status=400)


@api_view(['GET'])
def current_user(request):
    """LOGIN AUTHENTICATION"""

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def user_create(request):
    """USER CREATION"""

    serializer = UserSerializerWithToken(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def ClosestVendor(request):
    """ TO GET THE NEAREST VENDORS """
    latitude_user = request.GET['latitude']
    longitute_user = request.GET['longitude']
    # CURRENTLY SET BY ME CAN BE ADJUSTED BY USER LATER
    raidus_of_action = 1000
    response = Distance_between_user_and_vendors(latitude_user, longitute_user, raidus_of_action)

    return Response(response, status=200)

@api_view(['POST'])
def Set_budget_spent(request):
    new_budget_spent = request.POST.get('budget_spent')
    username = request.POST.get('username')
    user = User.objects.get(username=username)
    student = user.student
    user.student.budget_spent = new_budget_spent
    student.save()
    return Response(status=200)

@api_view(['POST'])
def ChangePassword(request):
    username = request.data.get("username")
    user = User.objects.get(username=username)
    password_serlizer = ChangePasswordSerializer(data=request.data)
    if password_serlizer.is_valid():
        if user.check_password(password_serlizer.data.get("old_password")):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password_serlizer.data.get("new_password"))
        user.save()
        response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
        return Response(response)

@api_view(['POST'])
def Return_Transcations(request):
    username = request.POST.get('username')
    user = User.objects.get(username=username)
    All_transcation = Transcations.objects.filter(FROM=user)
    transcation  = []
    for trans in All_transcation:
        current_trans = []
        current_trans.append(trans.TO.username)
        current_trans.append(trans.AMOUNT)
        current_trans.append(trans.DATE_TIME)
        transcation.append(current_trans)

    response = {"Transcations":transcation,'code':status.HTTP_200_OK}

    return Response(response)




@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def new_signup(request):
    """STUDENT SIGN UP"""

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
    """ VENDOR SIGNUP"""

    user_serializer = UserSerializerWithToken(data=request.data)
    vendor_serializer = VendorSerializer(data=request.data)

    if user_serializer.is_valid() and vendor_serializer.is_valid():
        user = user_serializer.save()
        vendor_serializer.save(user=user)
        response = {
            "user": user_serializer.data,
            "vendor": vendor_serializer.data
        }
        return Response(response, status=status.HTTP_201_CREATED)
    print('user_serializer.is_valid():')
    print(user_serializer.is_valid())
    print('vendor_serializer.is_valid():')
    print(vendor_serializer.is_valid())
    errors = {
        "user": user_serializer.errors,
        "vendors": vendor_serializer.errors
    }
    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def Mess_menu_upload(request):
    """ FILE UPLOAD AND MANGEMNET"""

    username = request.POST.get('username')
    parser_classes = [FileUploadParser]
    file_obj = request.data['file']
    if len(file_obj) != 0:
        handle_uploaded_file(file_obj, username)
        response = {
            "User": username
        }
        return Response(response, status=204)
    else:
        user = User.objects.get(username=username)
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


@api_view(['GET'])
def recommend(request):
    """ RECOMMENDATION ENGINE"""

    # Fetch the required data
    user = request.user
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
