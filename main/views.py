import requests
import json
from datetime import datetime
import time
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.decorators import (
    api_view, permission_classes
)
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from .models import Menu, Student, Transcations, Vendor
from .recommend import recommend as recommend_dish
from .serializers import (
    ChangePasswordSerializer, StudentSerializer, UserSerializer,
    UserSerializerWithToken, VendorSerializer
)
from .utility import (
    Distance_between_user_and_vendors, get_restaurants, handle_uploaded_file
)
import uuid


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


@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def closest_vendor(request):
    """ TO GET THE NEAREST VENDORS """
    print(request.data)
    latitude_user = request.data.get('latitude')
    longitute_user = request.data.get('longitude')
    # CURRENTLY SET BY ME CAN BE ADJUSTED BY USER LATER
    raidus_of_action = 1000
    response = Distance_between_user_and_vendors(latitude_user, longitute_user, raidus_of_action)

    return Response(response, status=200)


@api_view(['POST'])
def set_budget_spent(request):
    user = request.user
    student = user.student
    new_budget_spent = student.budget_total - int(request.data.get('budget'))
    student.budget_total = int(request.data.get('budget'))
    student.budget_spent += new_budget_spent
    student.save()
    resp = {
            "budget": student.budget_total
    }
    return JsonResponse(resp, safe=False)


@api_view(['POST'])
def change_password(request):
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


@api_view(['Get'])
def get_preferred_vendors(request):
    vendor_usernames = request.user.student.preferred_vendors.split(",")
    vendor_users = User.objects.filter(username__in=vendor_usernames)
    vendors = Vendor.objects.filter(user__in=vendor_users)
    resp = {
        "vendors": [{"username": v.user.username, "name": v.name} for v in list(vendors)]
    }
    return JsonResponse(resp, safe=False)


def account_creation(request):
    return uuid.uuid1(), uuid.uuid4()


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
        get_restaurants(request.data["preferred_restaurants"], user.username)
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
def mess_menu_upload(request):
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
    preferred_cuisines = user.student.preferred_cuisines
    dislikes = user.student.not_preferred

    today = datetime.now().strftime("%w")
    try:
        mess_menu = Menu.objects.get(student=student, day=int(today)+1, time="lunch").dishes
    except ObjectDoesNotExist:
        # object does not exists
        return JsonResponse({'status': 'failure'}, status=404)

    restrs = [{"name": "abc", "price": 120}, {"name": "def", "price": 300}]

    # Get the recommendation
    recommendation = recommend_dish(budget_total, budget_spent, restrs, dislikes, mess_menu)

    return JsonResponse(recommendation)

# Transaction Endpoints

@api_view(['POST'])
def make_transaction(request):
    vendor_username = request.data.get('username')
    transfer_amount = request.data.get('amount')
    vendor_user = User.objects.get(username=vendor_username)
    vendor = Vendor.objects.get(user=vendor_user)
    user = request.user
    student = user.student

    reciever = vendor_user
    Transcations(sender=request.user, reciever=reciever, amount=transfer_amount).save()
    student.budget_total = student.budget_total - transfer_amount
    student.budget_spent += transfer_amount
    student.save()
    return JsonResponse(200, safe=False)


@api_view(['GET'])
def get_transactions(request):
    transactions = Transcations.objects.filter(reciever=request.user)
    res = []
    for trans in transactions:
        res.append({'Sender':trans.sender.username,'Date':trans.timestamp.date(),'Amount':trans.amount})

    data = {'Transactions':res}
    return JsonResponse(data)


@api_view(['POST'])
def add_balance(request):
    transfer_amount = request.data.get('amount')
    user = request.user
    student = user.student
    student.budget_total = student.budget_total + transfer_amount
    student.save()
    return JsonResponse({'status':'200'})

@api_view(['Get'])
def get_balance(request):
    balance = request.user.student.budget_total
    data = {'Balance':balance}
    return JsonResponse(data)
