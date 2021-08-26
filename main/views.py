import requests
import json
from datetime import datetime

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
def closest_vendor(request):
    """ TO GET THE NEAREST VENDORS """
    latitude_user = request.GET['latitude']
    longitute_user = request.GET['longitude']
    # CURRENTLY SET BY ME CAN BE ADJUSTED BY USER LATER
    raidus_of_action = 1000
    response = Distance_between_user_and_vendors(latitude_user, longitute_user, raidus_of_action)

    return Response(response, status=200)


@api_view(['POST'])
def set_budget_spent(request):
    user = request.user
    student = user.student
    new_budget_spent = student.budget_total - int(request.data.get('budget'))
    student.budget_spent = new_budget_spent
    student.save()
    return Response(status=200)


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


@api_view(['POST'])
def return_transcations(request):
    username = request.POST.get('username')
    user = User.objects.get(username=username)
    all_transcation = Transcations.objects.filter(FROM=user)
    transcation = []
    for trans in all_transcation:
        current_trans = []
        current_trans.append(trans.TO.username)
        current_trans.append(trans.AMOUNT)
        current_trans.append(trans.DATE_TIME)
        transcation.append(current_trans)

    response = {"Transcations": transcation, 'code': status.HTTP_200_OK}

    return Response(response)


def account_creation(request):

    url = "https://fusion.preprod.zeta.in/api/v1/ifi/140793/applications/newIndividual"

    data = {
        "ifiID": "140793",
        "individualType": "REAL",
        "firstName": request.data.get("name"),
        "lastName": request.data.get("last_name"),
        "dob": {
            "year": request.data.get("DOB_year"),
            "month": request.data.get("DOB_month"),
            "day": request.data.get("DOB_date")
        },
        "kycDetails": {
            "kycStatus": "MINIMAL",
            "kycStatusPostExpiry": "string",
            "kycAttributes": {},
            "authData": {
                "PAN": request.data.get("PAN_number")
            },
            "authType": "PAN"
        },
        "vectors": [
            {
            "type": "p",
            "value": request.data.get("phone_no"),
            "isVerified": False
            }
        ]
    }
    payload = json.dumps(data)
    headers = {
        'X-Zeta-AuthToken': 'eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwidGFnIjoiNGNfLWdmV3pFTGg2bWZrSzByQjhEdyIsImFsZyI6IkExMjhHQ01LVyIsIml2IjoiM0lQS2RuaEI4RU9yQVhKRyJ9.w80fhzwFm8GnnZ1spk26SxQ2yf-XqCctikmV8MLYVxc.GtomDrqhlBj_rX05elWovA.A1yTzH7PNo66evnIpUqg7AkeHmTFGUmSst7WPDannMJBWX9b7jQ2H1gvySYNNKh3RTj-KyBow-Iaw7hGLTDSuc8As0ri7oDbC20-WBKmNscbFqMk0sEeMZScNFl8CwD935JXkxhAuWW7yq1Cxfo715SUPHexXx2b69JEEbbfBSwAGOCoXkmTNz562m_UUx9uvW9LEl3i16m6pxRmrp-7beFBb9Wr5DXBT0MI6NNS-vmjtcAxS6e7G-Y8nu5cNCKcpkrvGd6bw1STYW5oGNUtcxJWGpu844CNyKHpiEEoO2OVMYW-DTBJQ3qXRu_EIlCBJy_UMa8cXeVoxSKud6mAcB_jZrrxDP_L7kcMuwZfMuXpiWh4gJH4UiR3uECy5sUm.5FPBMDVsRfrl9XKklFSHRw',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # Bundle begin from here
    url_bundle = "https://fusion.preprod.zeta.in/api/v1/ifi/140793/bundles/fee9ee2d-14d5-4f92-96f2-401b4da39325/issueBundle"
    response_data = response.json()
    accountHolderID = response_data['individualID']
    name = "Kartik"
    data_bundle = {
        "ifiID": "140793",
        "accountHolderID": accountHolderID,
        "name": name,
        "phoneNumber": request.data.get("phone_no")
    }
    payload_bundle = json.dumps(data_bundle)
    response_bundle = requests.request("POST", url_bundle, headers=headers, data=payload_bundle)

    if response_bundle.status_code == 200:
        return accountHolderID
    else:
        return None





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
        mess_menu = Menu.objects.get(student=student, day=today, time="lunch").dishes
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
    ifiID = ""
    X_Zeta_AuthToken = ""
    amount = request.data.get("amount")
    transferCode = ""
    debitAccountID = request.user.accountID
    creditAccountID = request.data.get("creditAccountID")

    url = "https://api.preprod.zeta.in/api/v1/ifi/{ifiID}/transfers".format(ifiID)
    data = {
        "ifiID": ifiID,
        "X-Zeta-AuthToken": X_Zeta_AuthToken,
        "amount": {
            "currency": "INR",
            "amount": amount
        },
        "transferCode": transferCode,
        "debitAccountID": debitAccountID,
        "creditAccountID": creditAccountID,
        "remarks": "TEST"
    }

    response = requests.post(url, data).json()

    if (response["status"] == "SUCCESS"):
        reciever = Vendor.objects.get(accountID = request.data.get("creditAccountID"))
        Transcations(sender=request.user, reciever=reciever, amount=amount).save()
        return JsonResponse(response)

    return JsonResponse(response)
    pass


@api_view(['GET'])
def get_transactions(request):
    transactions = Transcations.objects.filter(reciever=request.user)
    return JsonResponse(transactions)
    pass
